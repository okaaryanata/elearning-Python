DROP DATABASE elibrary;
CREATE DATABASE elibrary;

-- View data
select * from public.buku;
select * from public.peminjaman;
select * from public.user;

-- add data to buku
insert into buku(judul,tahunterbit,pengarang) values ('testjudul',1998,'kasnadi');
insert into buku(judul,tahunterbit,pengarang) values ('testjudul',1998,'kasnadi');
insert into buku(judul,tahunterbit,pengarang) values ('testjudul',1998,'kasnadi');
insert into buku(judul,tahunterbit,pengarang) values ('testjudul',1998,'kasnadi');


-- add data to user
insert into public.user(name,email,password) values ('kasnadi1','kasnadi1@gmail.com','kasnadi1');
insert into public.user(name,email,password) values ('kasnadi2','kasnadi2@gmail.com','kasnadi2');