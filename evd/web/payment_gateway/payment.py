#from java.util.zip import Checksum

#from com import *
#import pdb;pdb.set_trace()
import sys

sys.path.append("web/payment_gateway/TechProUtil_out.jar")
from com import *

transaction_id = sys.argv[1]
amount = sys.argv[2]

objTranDetails = CheckSumRequestBean();
objTranDetails.setStrMerchantTranId(transaction_id);
objTranDetails.setStrMarketCode('L3633');
objTranDetails.setStrAccountNo('1');
objTranDetails.setStrAmt(amount);
objTranDetails.setStrBankCode('120');
objTranDetails.setStrPropertyPath('web/payment_gateway/MERCHA.PRO');

util = TPSLUtil()
strMsg = util.transactionRequestMessage(objTranDetails);
print strMsg
