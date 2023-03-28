import json
import requests
import statistics
import datetime
import io
import csv

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)

suiRPC=''
suiRPCmethod='{"jsonrpc": "2.0","id": 1,"method": "sui_getLatestSuiSystemState","params": ["0x5"]}'
telegramBotSecret=''
telegramChatId=''
telegramAPI='https://api.telegram.org/bot'+telegramBotSecret

suiRequest = requests.post(suiRPC, data=suiRPCmethod, headers={'content-type': 'application/json'})

suiResult=suiRequest.json()['result']
activeValidators=suiResult['activeValidators']
referenceGasPrice=suiRequest.json()['result']['referenceGasPrice']
numberValidators=len(activeValidators)

nextEpochGasPriceList=[]
quantnodeNextEpochGasPrice=0
totalVotingPower=10000
quorumVotingPower=6667
quorumCounter=0
nextEpochGasPriceReferal=0

for i in sorted(activeValidators, key=lambda item: item['nextEpochGasPrice']):
    nextEpochGasPriceList+=[i['nextEpochGasPrice']]
    if i['name']=='QuantNode':
        quantnodeNextEpochGasPrice=i['nextEpochGasPrice']
    if quorumCounter<quorumVotingPower:
        nextEpochGasPriceReferal=i['nextEpochGasPrice']
        quorumCounter+=i['votingPower']

nextEpochGasPriceMin=min(nextEpochGasPriceList)
nextEpochGasPriceMax=max(nextEpochGasPriceList)
nextEpochGasPriceMean=round(statistics.mean(nextEpochGasPriceList))
nextEpochGasPriceMedian=round(statistics.median(nextEpochGasPriceList))

countdown=datetime.datetime.fromtimestamp(suiResult['epochStartTimestampMs']/1000)+datetime.timedelta(milliseconds=+suiResult['epochDurationMs'])-datetime.datetime.now()

telegramMessage="<b>EpochNumber= "+str(suiRequest.json()['result']['epoch'])+'</b>'+\
"\n"+strfdelta(countdown, "{hours} hr {minutes} min {seconds} sec to the new epoch")+\
"\nReferenceGasPrice= "+str(suiRequest.json()['result']['referenceGasPrice'])+\
"\nNumberOfValidators= "+str(numberValidators)+\
"\nNextEpochGasPrice Min= "+str(nextEpochGasPriceMin)+\
"\nNextEpochGasPrice Max= "+str(nextEpochGasPriceMax)+\
"\nNextEpochGasPrice Mean= "+str(nextEpochGasPriceMean)+\
"\nNextEpochGasPrice Median= "+str(nextEpochGasPriceMedian)+\
"\n<b>NextEpochGasPrice Referal= "+str(nextEpochGasPriceReferal)+'</b>'+\
"\n<b>QuantNode's NextEpochGasPrice= " +str(quantnodeNextEpochGasPrice)+'</b>'

csvHeader=['suiAddress','name','votingPower','gasPrice',
            'commissionRate','nextEpochStake','nextEpochGasPrice','nextEpochCommissionRate',
            'stakingPoolSuiBalance','rewardsPool','poolTokenBalance','pendingStake',
            'pendingTotalSuiWithdraw','pendingPoolTokenWithdraw','epoch','storageFund',
            'referenceGasPrice','epochStartTimestampMs','stakeSubsidyEpochCounter','stakeSubsidyBalance',
            'stakeSubsidyCurrentEpochAmount','totalStake','pendingActiveValidatorsSize','validatorCandidatesSize',
            'numberValidators','nextEpochGasPriceReferal']
csvRows=[]

for i in range(0, numberValidators):
    csvRows.append([activeValidators[i]['suiAddress'],activeValidators[i]['name'],activeValidators[i]['votingPower'],activeValidators[i]['gasPrice'],
    activeValidators[i]['commissionRate'],activeValidators[i]['nextEpochStake'],activeValidators[i]['nextEpochGasPrice'],activeValidators[i]['nextEpochCommissionRate'],
    activeValidators[i]['stakingPoolSuiBalance'],activeValidators[i]['rewardsPool'],activeValidators[i]['poolTokenBalance'],activeValidators[i]['pendingStake'],
    activeValidators[i]['pendingTotalSuiWithdraw'],activeValidators[i]['pendingPoolTokenWithdraw'],suiResult['epoch'],suiResult['storageFund'],
    suiResult['referenceGasPrice'],suiResult['epochStartTimestampMs'],suiResult['stakeSubsidyEpochCounter'],suiResult['stakeSubsidyBalance'],
    suiResult['stakeSubsidyCurrentEpochAmount'],suiResult['totalStake'],suiResult['pendingActiveValidatorsSize'],suiResult['validatorCandidatesSize'],
    numberValidators,nextEpochGasPriceReferal])

csvFile=io.StringIO(newline='')

csvWriter = csv.writer(csvFile) 
csvWriter.writerow(csvHeader) 
csvWriter.writerows(csvRows)

suiData = {
    'chat_id': telegramChatId,
    'parse_mode': 'HTML',
    'caption': telegramMessage
    }

suiFiles = {
    'document': ('sui-'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'.csv', csvFile.getvalue(), 'text/csv')
}

telegramRequest=requests.post(telegramAPI+'/sendDocument?chat_id='+telegramChatId, files=suiFiles, data=suiData)

print(telegramMessage)
print(telegramRequest)
print(telegramRequest.text)
