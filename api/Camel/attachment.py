from flask_restful import request, reqparse
from Camel import CamelResource
from Camel.auth import login_required
from Camel import config

from os import path
from pathlib import Path
from uuid import uuid4

class Attachment(CamelResource):
    def __init__(self):
        upload_conf = config['uploads']
        self.reqparse = reqparse.RequestParser()
        self.tmp_uploads = Path(upload_conf['TMP'])
        self.tmp_uploads.mkdir(parents=True, exist_ok=True)

        ##POST arguments
        self.reqparse.add_argument('uuid', type = str)

    @login_required
    def post(self):
        uploadedFile = request.files['file']
        uuid = str(uuid4())
        target = str(self.tmp_uploads.joinpath(uuid))
        uploadedFile.save(target)

        return {'uuid': uuid}
