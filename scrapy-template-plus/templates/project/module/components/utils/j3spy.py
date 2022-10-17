import random

from anti_useragent.utils.cipers import generate_cipher
from anti_useragent.utils.scrapy_contextfactory import Ja3ScrapyClientContextFactory
from twisted.internet.ssl import CertificateOptions, AcceptableCiphers


class Ja3SpyClientContextFactory(Ja3ScrapyClientContextFactory):

    def getCertificateOptions(self):
        tls_ciphers = generate_cipher()
        tls_ciphers = ':'.join(random.sample(tls_ciphers.split(':'), random.randint(5, 8)))
        self.tls_ciphers = AcceptableCiphers.fromOpenSSLCipherString(tls_ciphers)
        return CertificateOptions(
            verify=False,
            method=getattr(self, 'method', getattr(self, '_ssl_method', None)),
            fixBrokenPeers=True,
            acceptableCiphers=self.tls_ciphers
        )
