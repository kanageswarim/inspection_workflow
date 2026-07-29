INSERT INTO Requests (Date, Cell, MachineNumber, MachineName, RequestCategory,
                       RequestType, Priority, MachineStatus, ReasonForInspection,
                       MachineIncharge, Stage2FlagRequested, Status)
VALUES ('2026-06-15', 'Welding', 'WEL-03', 'Dories', 'Safety',
        'Breakdown', 'High', 'Working', 'Guard sensor failure',
        'Sri Varun', 'Yes', 'Completed');

INSERT INTO InspectionStage1 (RequestID, StartDate, EndDate, Status, InspectedBy, Remarks, Stage2Required)
VALUES (751, '2026-06-16', '2026-06-17', 'Fail', 'Ravi Kumar', 'Confirmed defect', 'Yes');

INSERT INTO InspectionStage2 (InspectionID, StartDate, EndDate, Status, InspectedBy, Remarks)
VALUES (
  (SELECT InspectionID FROM InspectionStage1 ORDER BY InspectionID DESC LIMIT 1),
  '2026-06-19', '2026-06-20', 'Pass', 'Sri Priya', 'Part replaced'
);