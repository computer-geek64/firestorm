-- populate.sql
-- Delete rows if they already exist
DELETE FROM "priority" CASCADE;
DELETE FROM "status" CASCADE;

-- Drop constraints
ALTER TABLE "priority" DROP CONSTRAINT IF EXISTS "row_lock";
ALTER TABLE "status" DROP CONSTRAINT IF EXISTS "row_lock";


-- Insert into table priority
INSERT INTO "priority" (
                "label"
            )
     VALUES (
                'low'
            ),
            (
                'medium'
            ),
            (
                'high'
            ),
            (
                'critical'
            );

-- Lock table priority with row_lock constraint
ALTER TABLE "priority" ADD CONSTRAINT "row_lock" CHECK ("id" <= 4);

-- Insert into table status
INSERT INTO "status" (
                "label",
                "percentage"
            )
     VALUES
            (
                'not started',
                0
            ),
            (
                'started',
                0.1
            ),
            (
                'halfway',
                0.5
            ),
            (
                'almost finished',
                0.75
            ),
            (
                'completed',
                1
            );

-- Lock table status with row_lock constraint
ALTER TABLE "status" ADD CONSTRAINT "row_lock" CHECK ("id" <= 5);
