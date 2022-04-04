from typing import Dict

from bs4 import BeautifulSoup
import magic
import requests
from websocket import create_connection, WebSocket
import time
from headers import sock_get_headers, plain_cookies, cookies_to_str, create_socket_headers, better_cookies, \
    upload_file_headers
import json
from threading import Lock, Thread, main_thread


def extractCSRF(dochtml):
    soup = BeautifulSoup(dochtml, 'html.parser')
    tag = soup.find('meta', attrs={'name': "ol-csrfToken"})
    return tag['content']


class OverleafClient:
    def __init__(self, sess_id: str, proj_id: str):
        res = requests.get("https://www.overleaf.com/project/%s" % proj_id, headers=sock_get_headers(proj_id),
                           cookies=plain_cookies(sess_id))
        gclb: str = res.cookies['GCLB']
        csrf: str = extractCSRF(res.text)
        tfreeze = int(time.time() * 1000)
        sock_create = requests.get("https://www.overleaf.com/socket.io/1/?t=%s" % tfreeze,
                                   headers=sock_get_headers(proj_id), cookies=better_cookies(sess_id, gclb))

        sock_info = sock_create.text.split(",")[0]
        sock_endpoint_id = sock_info.split(":")[0]
        ws: WebSocket = create_connection("wss://www.overleaf.com/socket.io/1/websocket/%s" % sock_endpoint_id,
                                          host="www.overleaf.com",
                                          origin="https://www.overleaf.com",
                                          cookie=cookies_to_str(better_cookies(sess_id, gclb)),
                                          headers=create_socket_headers)
        ws.recv()
        ws.recv()
        ws.send('5:1+::{"name":"joinProject","args":[{"project_id":"%s"}]}' % proj_id)

        self.ws = ws
        self.dirData = json.loads(ws.recv()[6:])[1]['rootFolder'][0]
        self.socket_lock = Lock()
        self.sess_id = sess_id
        self.proj_id = proj_id
        self.gclb = gclb
        self.hrt = HeartBeatThread(self)
        self.hrt.start()
        self.csrf = csrf
        self.currentDocId = None
        self.messageId = 1

    def getFileId(self, path: str) -> str:
        """
        get file id given a path

        :param path: path of file
        :return: _id value for references
        """
        if path == '':
            raise FileNotFoundError("root dir is not a file")
        partpath = path.split("/")
        cdir = self.dirData
        while len(partpath) > 1:
            next_folder = partpath.pop(0)
            cur_folders = cdir['folders']
            for folder in cur_folders:
                if folder['name'] == next_folder:
                    nextdir = folder
            if nextdir is None:
                raise FileNotFoundError("could not find folder: %s" % next_folder)
            cdir = nextdir
        folderfiles = cdir['docs'] + cdir['fileRefs']
        for file in folderfiles:
            if file['name'] == partpath[0]:
                return file['_id']

    def getFolderId(self, path: str) -> str:
        a = self.listdir(path + "/")
        return a['_id']

    def heartbeat(self):
        with self.socket_lock as sk:
            self.ws.send("2::")
            data = self.ws.recv()
            while data != '2::':
                data = self.ws.recv()

    def listdir(self, dirpath: str):
        """
        get raw dir data

        :param dirpath: dir to obstain
        :return: json data
        """
        partpath = dirpath.split("/")
        cdir = self.dirData
        while len(partpath) > 1:
            next_folder = partpath.pop(0)
            cur_folders = cdir['folders']
            for folder in cur_folders:
                if folder['name'] == next_folder:
                    nextdir = folder
            if nextdir is None:
                raise FileNotFoundError("could not find folder: %s" % next_folder)
            cdir = nextdir
        return cdir

    def resync(self):
        """
        resync project space

        :return: nothing
        """
        with self.socket_lock as sk:
            self.ws.send('5:1+::{"name":"joinProject","args":[{"project_id":"%s"}]}' % self.proj_id)
            data = self.ws.recv()
            while data[:6] != "6:::1+":
                data = self.ws.recv()
            self.messageId = 2
        self.dirData = json.loads(data[6:])[1]['rootFolder'][0]

    def upload_data(self, datasrc: str, targetpath: str, overwrite=False) -> str:
        """
        uploads data to the repository

        :param datasrc: local path to data (abspath prefered)
        :param targetpath: target path in overleaf dir
        :param overwrite: error on namespace conflict or overwrite
        :return: file id of new file
        """
        tokenized_path = targetpath.split('/')
        parent_dir = '/'.join(tokenized_path[:-1])
        new_name = tokenized_path[-1]
        par_id = self.getFolderId(parent_dir)
        dtype = magic.from_file(datasrc, mime=True)

        resp = requests.post("https://www.overleaf.com/project/%s/upload?folder_id=%s" % (self.proj_id, par_id),
                             headers=upload_file_headers(self.proj_id, self.csrf),
                             cookies=better_cookies(self.sess_id, self.gclb),
                             data={"relativePath": "null", "name": new_name, 'type': dtype},
                             files={"qqfile": open(datasrc, "rb")})
        file_id: str = json.loads(resp.content)['entity_id']
        # app rename on item
        resp = requests.post("https://www.overleaf.com/project/%s/file/%s/rename" % (self.proj_id, file_id),
                             headers=upload_file_headers(self.proj_id, self.csrf),
                             cookies=better_cookies(self.sess_id, self.gclb),
                             data={'name': new_name})
        self.resync()
        return file_id

    def leaveDoc(self):
        if self.currentDocId is not None:
            with self.socket_lock as wk:
                self.ws.send('5:%s+::{"name":"leaveDoc","args":["%s"]}' % (self.messageId, self.currentDocId))
                data = self.ws.recv()
                while '6:::%s' % self.messageId not in data:
                    data = self.ws.recv()
                self.messageId += 1
                self.currentDocId = None

    def readDoc(self, path, join=True):
        fileid = self.getFileId(path)
        self.leaveDoc()
        data = None
        with self.socket_lock as wk:
            self.ws.send('5:%s+::{"name":"joinDoc","args":["%s",{"encodeRanges":true}]}' % (self.messageId, fileid))
            data = self.ws.recv()
            while '6:::%s+' % self.messageId not in data:
                data = self.ws.recv()
            prefix = '6:::%s+' % self.messageId
            data = data[len(prefix):]
            self.messageId += 1
            self.currentDocId = fileid

        if not join:
            self.leaveDoc()
        return json.loads(data)[1]

    def updateCursor(self, row, col):
        if self.currentDocId is None:
            raise AssertionError('no current document selected to move cursor within.')

        with self.socket_lock as wk:
            self.ws.send(
                '5:::{"name":"clientTracking.updatePosition","args":[{"row":%s,"column":%s,"doc_id":"%s"}]}' % (
                    row, col, self.currentDocId))
            data = self.ws.recv()
            while '5:::' not in data:
                data = self.ws.recv()
            self.messageId += 1
        dataout = json.loads(data[4:])
        return dataout['args'][0]


class HeartBeatThread(Thread):
    def __init__(self, ref):
        Thread.__init__(self)
        self.cliref = ref

    def run(self):
        while main_thread().is_alive():
            for i in range(0, 20):
                if not main_thread().is_alive():
                    return
                time.sleep(1)
            self.cliref.heartbeat()
