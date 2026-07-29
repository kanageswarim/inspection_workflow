DELETE FROM InspectionStage2;
DELETE FROM InspectionStage1;
DELETE FROM Requests;
DELETE FROM sqlite_sequence WHERE name IN ('Requests', 'InspectionStage1', 'InspectionStage2');

SELECT COUNT(*) FROM Requests;
SELECT COUNT(*) FROM InspectionStage1;
SELECT COUNT(*) FROM InspectionStage2;