-- schema.sql
-- Drop tables if already exists
DROP TABLE IF EXISTS "priority" CASCADE;
DROP TABLE IF EXISTS "status" CASCADE;
DROP TABLE IF EXISTS "event" CASCADE;
DROP TABLE IF EXISTS "task" CASCADE;

-- Drop views if already exists
DROP VIEW IF EXISTS "calendar_view" CASCADE;


-- Create tables
-- Create table priority
CREATE TABLE "priority" (
    "id" SERIAL PRIMARY KEY,
    "label" VARCHAR NOT NULL
);

-- Create table status
CREATE TABLE "status" (
    "id" SERIAL PRIMARY KEY,
    "label" VARCHAR NOT NULL,
    "percentage" FLOAT
);

-- Create table event
CREATE TABLE "event" (
    "label" VARCHAR,
    "description" VARCHAR,
    "start_time" TIMESTAMP NOT NULL,
    "end_time" TIMESTAMP,
    "priority" INTEGER NOT NULL REFERENCES "priority" ("id") DEFAULT 1,
    "location" VARCHAR,
    "url" VARCHAR,
    PRIMARY KEY ("label", "end_time")
);

-- Create table task
CREATE TABLE "task" (
    "label" VARCHAR,
    "description" VARCHAR,
    "deadline" TIMESTAMP,
    "priority" INTEGER NOT NULL REFERENCES "priority" ("id") DEFAULT 1,
    "status" INTEGER NOT NULL REFERENCES "status" ("id") DEFAULT 1,
    "location" VARCHAR,
    "url" VARCHAR,
    PRIMARY KEY ("label", "deadline")
);


-- Create views
-- Create view calendar_view
CREATE VIEW "calendar_view"
         AS
     SELECT *
       FROM (
     SELECT 'event'
         AS "type",
            "e"."label"
         AS "label",
            "e"."description"
         AS "description",
            "e"."start_time"
         AS "start_time",
            "e"."end_time"
         AS "end_time",
            "p"."label"
         AS "priority",
            CASE
                WHEN current_timestamp <= "e"."start_time" THEN 0
                WHEN current_timestamp >= "e"."end_time" THEN 1
                ELSE extract(epoch FROM current_timestamp - "e"."start_time") / extract(epoch FROM "e"."end_time" - "e"."start_time")
            END
         AS "status",
            "e"."location"
         AS "location",
            "e"."url"
         AS "url"
       FROM "event"
         AS "e"
 INNER JOIN "priority"
         AS "p"
         ON "e"."priority" = "p"."id"
  UNION ALL
     SELECT 'task'
         AS "type",
            "t"."label"
         AS "label",
            "t"."description"
         AS "label",
            "t"."deadline"
         AS "start_time",
            "t"."deadline"
         AS "end_time",
            "p"."label"
         AS "priority",
            "s"."percentage"
         AS "status",
            "t"."location"
         AS "location",
            "t"."url"
         AS "url"
       FROM "task"
         AS "t"
 INNER JOIN "priority"
         AS "p"
         ON "t"."priority" = "p"."id"
 INNER JOIN "status"
         AS "s"
         ON "t"."status" = "s"."id") "unordered_calendar"
   ORDER BY "end_time" ASC,
            CASE
                WHEN "priority" = 'high' THEN 1
                WHEN "priority" = 'medium' THEN 2
                WHEN "priority" = 'low' THEN 3
            END ASC;
