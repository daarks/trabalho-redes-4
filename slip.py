class CamadaEnlace:
    ignore_checksum = False

    def __init__(self, linhas_seriais):
        self.enlaces = {}
        self.callback = None
        for ip_outra_ponta, linha_serial in linhas_seriais.items():
            enlace = Enlace(linha_serial)
            self.enlaces[ip_outra_ponta] = enlace
            enlace.registrar_recebedor(self._callback)

    def registrar_recebedor(self, callback):
        self.callback = callback

    def enviar(self, datagrama, next_hop):
        self.enlaces[next_hop].enviar(datagrama)

    def _callback(self, datagrama):
        if self.callback:
            self.callback(datagrama)


class Enlace:
    def __init__(self, linha_serial):
        self.linha_serial = linha_serial
        self.linha_serial.registrar_recebedor(self.__raw_recv)
        self.buffer = b''

    def registrar_recebedor(self, callback):
        self.callback = callback

    def enviar(self, datagrama):
        datagrama = datagrama.replace(b'\xdb', b'\xdb\xdd')
        datagrama = datagrama.replace(b'\xc0', b'\xdb\xdc')
        self.linha_serial.enviar(b'\xc0' + datagrama + b'\xc0')

    def __raw_recv(self, dados):
        dados = self.buffer + dados
        datagramas = dados.split(b'\xc0')
        self.buffer = datagramas[-1]
        for datagrama in datagramas[:-1]:
            if datagrama:
                try:
                    datagrama = datagrama.replace(b'\xdb\xdc', b'\xc0')
                    datagrama = datagrama.replace(b'\xdb\xdd', b'\xdb')
                    self.callback(datagrama)
                except:
                    import traceback
                    traceback.print_exc()
                finally:
                    datagrama = b''
