from flask import Flask, request, json, session, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_restful import marshal, fields
import datetime
from time import gmtime, strftime
from flask_cors import CORS, cross_origin
import os
import jwt
import requests
from requests.utils import quote

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:kumiskucing@localhost:5432/elibrary'
CORS(app, support_credentials=True)
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
jwtSecretKey = "kumiskucing"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    password = db.Column(db.String())

class Buku(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String())
    tahunterbit = db.Column(db.Integer())
    pengarang = db.Column(db.String())


class Peminjaman(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tanggalpinjam = db.Column(db.String())
    tanggalkembali = db.Column(db.String())
    id_buku = db.Column(db.Integer, db.ForeignKey('buku.id'))


@app.route('/')
def get():
    return "test", 201

# fungsi untuk login ke web
@app.route('/login', methods=['POST'])
def login():
    requestData = request.get_json()
    reqEmail = requestData.get('email')
    reqPassword = requestData.get('password')
    dataUser = User.query.filter_by(email=reqEmail, password=reqPassword).first()
    if dataUser:
        payload = {
            "id": dataUser.id,
            "secretcode": "kumiskucing"
        }
        encoded = jwt.encode(payload, jwtSecretKey,
                             algorithm='HS256').decode('utf-8')
        jsonFormat = {
            "token": encoded
        }
        userJson = json.dumps(jsonFormat)

        return userJson, 200
    else:
        return 'gagal', 404

# fungsi untuk menambahkan buku ke db
@app.route('/tambah-buku',methods=['POST'])
def tambahBuku():
    if request.method == 'POST':
        request_data = request.get_json()
        sent_data = Buku( #sent data
            judul = request_data.get('judul'),
            tahunterbit = request_data.get('tahunterbit'),
            pengarang = request_data.get('pengarang'),
        )
        #add data
        db.session.add(sent_data)
        db.session.commit()
        
        return 'berhasil',201
    else:
        return 'Method not allowed',405


@app.route('/pinjam-buku', methods=['POST'])
def pinjamBuku():
    request_data = request.get_json()
    decoded = jwt.decode(request.headers["Authorization"], jwtSecretKey, algorithm='HS256')
    idBuku = request_data.get('id_buku')
    userDB = User.query.filter_by(id=decoded["id"]).first() 
    bukuDB = Buku.query.filter_by(id=idBuku).first()
    
    if userDB:
        if bukuDB == None:
            return 'Buku tidak ditemukan',404
        else:
            sent_data = Peminjaman( #sent data
                user_id = userDB.id,
                tanggalpinjam = strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                id_buku = bukuDB.id,
            )
            #add data
            db.session.add(sent_data)
            db.session.commit()
            return 'Buku berhasil dipinjam',201
    else:
        return 'Please login',400

@app.route('/detail-buku', methods=['GET'])
def detailBuku():
    request_data = request.get_json()
    decoded = jwt.decode(request.headers["Authorization"], jwtSecretKey, algorithm='HS256')
    idBuku = request_data.get('id_buku')
    bukuDB = Buku.query.filter_by(id=idBuku).first()
    peminjamanDB = Peminjaman.query.filter_by(id_buku=idBuku)
    arrPeminjaman = []
    for x in peminjamanDB:
        idUser = x.user_id
        userDB = User.query.filter_by(id= idUser).first()
        peminjaman_json = {
            "user_name" : userDB.name,
            "tanggalpinjam" : x.tanggalpinjam,
            "tanggalkembali" : x.tanggalkembali
        }
        arrPeminjaman.append(peminjaman_json)

    if bukuDB:
        jsonFormat = {
            "judul": bukuDB.judul,
            "tahunterbit": bukuDB.tahunterbit,
            "pengarang": bukuDB.pengarang,
            "riwayat peminjaman" : arrPeminjaman
        }
        bukuJson = json.dumps(jsonFormat)
        return bukuJson, 200
    else:
        return 'Detail buku tidak ditemukan',404

@app.route('/semua-buku',methods=['GET'])
def semuaBuku():
    bukus = Buku.query.all()
    arrayBuku = []
    for buku in bukus:
        jsonFormat = {
            "id_buku" : buku.id,
            "judul": buku.judul,
            "tahunterbit": buku.tahunterbit,
            "pengarang": buku.pengarang
        }
        arrayBuku.append(jsonFormat)
    bukuJson = json.dumps(arrayBuku)
    return bukuJson, 201

@app.route('/kembali-buku', methods=['POST'])
def kembaliBuku():
    request_data = request.get_json()
    decoded = jwt.decode(request.headers["Authorization"], jwtSecretKey, algorithm='HS256')
    idPeminjaman = request_data.get('id_pinjam')
    peminjamanDB = Peminjaman.query.filter_by(id = idPeminjaman).first()
    if peminjamanDB:
        userDB = User.query.filter_by(id=decoded["id"]).first()
        if peminjamanDB.user_id == userDB.id :
            peminjamanDB.tanggalkembali = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            db.session.commit()
            return "Buku berhasil dikembalikan", 200
        else:
            return "Gagal mengembalikan",400
    else:
        return "peminjaman tidak ditemukan", 404


if __name__ == '__main__':
    app.run(debug=os.getenv("DEBUG"), host=os.getenv(
        "HOST"), port=os.getenv("PORT"))