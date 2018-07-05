import requests, os, json

class BaseResource(object):
    def __init__(self, session, url):
        self._url = url
        self._method = 'POST'
        self._session = session

    def __getattr__(self, item):
        url = os.path.join(self._url, item)
        resource = BaseResource(self._session, url)
        setattr(self, item, resource)
        return resource

    def __call__(self, **kwargs):
        response = self._session.request(self._method, self._url, kwargs)
        return response

class Client(BaseResource):
    def __init__(self, ip, port, client_id=None, client_secret=None):
        # Generate the jwt
        session = requests.Session()

        if client_id and client_secret:
            jwt = self._generate_jwt(client_id, client_secret)
            session.headers['Authorization'] = 'Bearer {}'.format(jwt)

        # Generate the url
        protocol = "https" if port == 443 else "http"
        url = "{protocol}://{ip}:{port}/restmachine".format(protocol=protocol, ip=ip, port=port)

        super(Client, self).__init__(session, url)


    def _generate_jwt(self, client_id, client_secret):
        params = {
            'grant_type':'client_credentials',
            'response_type':'id_token',
            'client_id':client_id,
            'client_secret':client_secret
        }
        response = requests.post('https://itsyou.online/v1/oauth/access_token', params=params)
        response.raise_for_status()
        return response.content.decode('utf-8')

    def load_swagger(self):
        response = self._session.post(self._url + '/system/docgenerator/prepareCatalog')
        response.raise_for_status()
        swagger = response.json()

        for methodpath, methodspec in swagger['paths'].items():
            api = self
            for path in methodpath.split('/')[1:]:
                api = getattr(api, path)
            method = 'post'
            if 'post' not in methodspec and methodspec:
                method = list(methodspec.keys())[0]
            api._method = method
            docstring = methodspec[method]['description']
            for param in methodspec[method].get('parameters', list()):
                param['type'] = param['type'] if 'type' in param else str(
                    param.get('$ref', 'unknown'))
                docstring += """
                :param %(name)s: %(description)s required %(required)s
                :type %(name)s: %(type)s""" % param
            api.__doc__ = docstring

        return swagger