create database gui;
create user gui with password 'gui1';
ALTER ROLE gui SET client_encoding TO 'utf8';
ALTER ROLE gui SET default_transaction_isolation TO 'read committed';
ALTER ROLE gui SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE gui TO gui;
