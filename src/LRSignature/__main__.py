'''
Created on Jun 14, 2011

@author: jklo
'''
import types
import sys

class InvalidJSONError(ValueError):
    def __init__(self, **kwargs):
        ValueError.__init__(self, **kwargs)
        

class PipeTool(object):

    def __init__(self):
        
        from sign.Sign import Sign_0_21
        self.args = self.parseArgs()
        
        self.signtool = Sign_0_21(privateKeyID=self.args.key, 
                                  passphrase=self.args.passphrase,  
                                  gnupgHome=self.args.gnupghome, 
                                  gpgbin=self.args.gpgbin, publicKeyLocations=self.args.key_location)
        pass

    def run(self):
        import json
        
        rawInput = self.readInput()
        envelopeList = self.parseInput(rawInput)
        signedList = self.signEnvelopes(envelopeList, is_test_data=True)
        
        if self.args.publish_url != None:
            self.publishEnvelopes(signedList)
        else:
            print json.dumps(signedList)
            

    def _set_test_key(self, envelope, remove=True):
        rmcount = 0
        
        if envelope.has_key("keys"):
            for item in envelope["keys"]:
                if item == "lr-test-data":
                    rmcount += 1
        if remove:
            while rmcount > 0:
                try:
                    envelope["keys"].remove("lr-test-data")
                except:
                    pass
                rmcount += -1
        elif not remove and rmcount == 0:
            envelope["keys"].append("lr-test-data")
            
        return envelope

    def _chunkList(self, fullList = [], chunkSize=10):
        numElements = len(fullList)
        for start in range(0, numElements, chunkSize):
            end = start+chunkSize
            if end > numElements:
                end = numElements
            yield fullList[start:end]

    def publishEnvelopes(self, envelopes):
        import urllib2,json
        req = urllib2.Request(self.args.publish_url, headers={"Content-type": "application/json; charset=utf-8"})
        status = []
        for chunk in self._chunkList(envelopes, self.args.publish_chunksize):
            res = urllib2.urlopen(req, data=json.dumps({ "documents":chunk }), timeout=self.args.publish_timeout)
            status.append(json.load(res))
            
        print json.dumps(status)
    
    def signEnvelopes(self, envelopes, is_test_data=True):
        signedEnvelopes = []
        for envelope in envelopes:
            self._set_test_key(envelope, remove=not is_test_data)
            signed = self.signtool.sign(envelope)
            signedEnvelopes.append(signed)
        return signedEnvelopes

    def parseArgs(self):
        import argparse, json
        parser = argparse.ArgumentParser(description='Sign files for Learning Registry')
        parser.add_argument('--key', help='PGP Private Key ID', required=True)
        parser.add_argument('--key-location', help='Location the PGP Public Key can be downloaded from', required=True, action="append")
        parser.add_argument('--passphrase', help='Passphrase for PGP Private Key', default=None)
        parser.add_argument('--gpgbin', help='Path to GPG binary', default="gpg")
        parser.add_argument('--gnupghome', help='Path to GPG home directory', default="~/.gnupg")
        parser.add_argument('--lr-test-data', help='Publish as lr test data, default is True', default="True")
        parser.add_argument('--publish-url', help='URL of publish service on node to send envelopes, default STDOUT', default=None)
        parser.add_argument('--publish-chunksize', help='publish chunksize, default 25', type=int, default=25)
        parser.add_argument('--publish-timeout', help='publish timeout in seconds, default 300', type=int, default=300)
#        parser.add_argument('--config', help='JSON Configuration file', default=None, type=argparse.FileType('r'))
        args = parser.parse_args()
        
#        config = {}
#        
#        if args.config != None:
#            config = json.load(args.config)
#        
#        for (k, v) in args:
#            config[k] = v
#            
        
        return args


    def parseInput(self, input=None):
        import json
 
        if input is not None:
            try:
                jsobject = json.loads(input)
                
                if isinstance(jsobject, types.DictionaryType):
                    return [jsobject]
                elif isinstance(jsobject, types.ListType):
                    return jsobject
                
            except Exception, e:
                raise InvalidJSONError(e)
        return None
        


    def readInput(self):
        import json
        pipedInput = ''
        try:
            while True:
                pipedInput += raw_input()
                
        except EOFError:
            pass
    
        return pipedInput
    

if __name__ == "__main__":
    tool = PipeTool()
    tool.run()
