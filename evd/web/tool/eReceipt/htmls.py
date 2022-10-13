def make_single_html_page(billno, name, address, amount, date, num_to_word):
	data = """<html>
		<body style="padding: 60px">
			<div style="width: 98%; height: 550px; border: 2px solid #000; position: absolute; top: 73px; left: 0px"></div>
			<div style="text-align: center; font-size: 14px; padding-top: 7px;">&nbsp</div>
        	<div width="1200" height="300" style="overflow: hidden; position: relative;">
            	<div style="border-bottom: 1px dashed #000; margin-bottom: 10px; padding-bottom: 20px">
                	<img alt='Logo' src="web/tool/eReceipt/logo.png" style="float: left; display: block; width: 129px; height: 84px; margin-left: 20px;" />
	                <div style="display: block; float: right; margin-top: 26px;">
    	                <div style="font-size: 14px;margin-left: 9px">No: PG-"""+str(int(billno))+""" </div>
        	            <div style="font-size: 14px;">Date: """+str(date)+"""</div>
            	    </div>
                	<div style="clear: both"></div>
	            </div>
    	    </div>
			<div>
            <div style="font-size: 14px;">Received with thanks from: """+name.strip()+"""</div>
            <div style="font-size: 14px;">Address: """+address.strip()+"""</div><br/>
            <div style="font-size: 14px;">On account of: Donation</div>
            <div style="font-size: 14px;">A sum of rupees (in words): """+num_to_word+"""</div>
            <div style="font-size: 14px;">Via payment gateway</div>
            <div style="font-size: 14px;">&#8377: """+str(int(amount))+"""</div>
            <div style="font-size: 14px; text-align:right; border-bottom: 1px dashed #000; padding-bottom: 10px; margin-bottom: 10px; padding-right: 100px;">Received By: &nbsp<img alt='Scan sign' src="web/tool/eReceipt/scan_sign.jpg" height="40" width="80"/></div>
			<div style='text-align:center;font-size: 14px;'>Address: 608, 27th Main Road, MCHS Colony, Stage 2, BTM 2nd Stage, Bengaluru, Karnataka 560076  Phone:080 4090 3939</div>
            <div style="font-size: 14px; text-align: center;">eVidyaloka.. is registered under Societies Acts 1860 & all donations are exempted u/s 80G of IT act Vide no. DIT(E)BLR/80G/278/AAATE4036C/ITO(E)-1/Vol 2012-2013 Dt. 30.10.2012 BANGALORE. PAN No. AAATE4036C</div>
			</div>
		</body>
	</html>"""

	return data

def adjust_html_to_multiple_receipts(billno, name, address, amount, date, num_to_word):
	data = """
			<div style="width: 98%; height: 550px; border: 2px solid #000; position: absolute; left: 0px"></div>
            <div style="padding: 0px 40px">
                <div style="text-align: center; font-size: 10px; padding-top: 7px;">&nbsp</div>
                <div width="1200" height="300" style="overflow: hidden; position: relative;">
                    <div style="border-bottom: 1px dashed #000; margin-bottom: 10px; padding-bottom: 20px">
                    <img alt='Logo' src="web/tool/eReceipt/logo.png" style="float: left; display: block; width: 129px; height: 70px; margin-left: 20px;" />
                    <div style="display: block; float: right; margin-top: 26px;">
                        <div style="font-size: 10px;margin-left: 9px">No: PG-"""+str(int(billno))+""" </div>
                        <div style="font-size: 10px;">Date: """+str(date)+"""</div>
                    </div>
                    <div style="clear: both"></div>
                </div>
            </div>
            <div>
                <div style="font-size: 10px;">Received with thanks from: """+name.strip()+"""</div>
                <div style="font-size: 10px;">Address: """+address.strip()+"""</div><br/>
                <div style="font-size: 10px;">On account of: Donation</div>
                <div style="font-size: 10px;">A sum of rupees (in words): """+num_to_word+"""</div>
                <div style="font-size: 10px;">Via payment gateway</div>
                <div style="font-size: 10px;">&#8377: """+str(int(amount))+"""</div>
                <div style="font-size: 10px; text-align:right; border-bottom: 1px dashed #000; padding-bottom: 10px; margin-bottom: 10px; padding-right: 100px;">Received By: &nbsp<img alt='Scan sign' src="web/tool/eReceipt/scan_sign.jpg" height="40" width="80"/></div>
                <div style='text-align:center;font-size: 10px;'>Address: 608, 27th Main Road, MCHS Colony, Stage 2, BTM 2nd Stage, Bengaluru, Karnataka 560076  Phone:080 4090 3939</div>
                <div style="font-size: 10px; text-align: center;">eVidyaloka.. is registered under Societies Acts 1860 & all donations are exempted u/s 80G of IT act Vide no. DIT(E)BLR/80G/278/AAATE4036C/ITO(E)-1/Vol 2012-2013 Dt. 30.10.2012 bANGALORE. PAN No. AAATE4036C</div>
            </div>
	"""
	
	return data
