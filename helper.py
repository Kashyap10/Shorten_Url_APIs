from config import Config
import jwt
import datetime
import pyshorteners
from baseconv import base62

class Helper():
    @staticmethod
    def encode_auth_token(userdata):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=10),
                'iat': datetime.datetime.utcnow(),
                'username': userdata['username'],
                'password':userdata['password']
            }
            return jwt.encode(
                payload,
                Config.SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, Config.SECRET_KEY,algorithms='HS256')
            return payload
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    @staticmethod
    def get_shorten_url(url):
        """
        This function will return short url of original url
        :param url: original url
        :return: short url
        """
        try:
            shorten = pyshorteners.Shortener()
            shortenurl = shorten.tinyurl.short(url)
            return shortenurl
        except Exception as e:
            return e

    @staticmethod
    def get_original_url(url):
        """
        This function will return original url of short url
        :param url: short url
        :return: original url
        """
        try:
            shorten = pyshorteners.Shortener()
            originalurl = shorten.tinyurl.expand(url)
            return originalurl
        except Exception as e:
            return e

    @staticmethod
    def short_url(lastid):
        """
        This function will generate short url based on last autoincremented id from table here we are adding 100000000000
        as we want to generate 7 character long unique id
        :param lastid: last autoincremented id from table
        :return: short url
        """
        number = lastid +100000000000
        bs62encoded = base62.encode(number)
        return 'https://abc.com/{id}'.format(id=str(bs62encoded))
