-- create.sql
-- Drop tables if already exists
DROP TABLE IF EXISTS "organization_type" CASCADE;
DROP TABLE IF EXISTS "organization" CASCADE;
DROP TABLE IF EXISTS "language" CASCADE;
DROP TABLE IF EXISTS "project" CASCADE;


-- Create tables
-- Create table organization type
CREATE TABLE "organization_type" (
    "label" VARCHAR (32) PRIMARY KEY
);

-- Create table organization
CREATE TABLE "organization" (
    "name" VARCHAR (64) PRIMARY KEY,
    "type" VARCHAR (32) NOT NULL REFERENCES "organization_type" ("label")
);

-- Create table language
CREATE TABLE "language" (
    "name" VARCHAR (32),
    "extension" VARCHAR (8),
    "color" VARCHAR (8)
);

-- Create table project
CREATE TABLE "project" (
    "name" VARCHAR (64) PRIMARY KEY,
    "description" VARCHAR (512) NOT NULL,
    "organization" VARCHAR (64) NOT NULL REFERENCES "organization" ("name"),
    "language" VARCHAR (32) REFERENCES "language" ("name"),
    "starred" BOOLEAN NOT NULL DEFAULT FALSE,
    "created" TIMESTAMP NOT NULL DEFAULT current_timestamp
);