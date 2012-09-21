import suds

## We need to patch suds.client.SoapClient because it doesn't throw an exception in case of bad authentication
class SudsClientPatched(suds.client.SoapClient):
     _oldFailed = suds.client.SoapClient.failed
     def failed(self, binding, error):
          if error.httpcode == 500:
               return SudsClientPatched._oldFailed(self, binding, error)
          else:
               raise error
suds.client.SoapClient = SudsClientPatched
## End patch

