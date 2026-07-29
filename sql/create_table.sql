CREATE TABLE Requests (
    RequestID INTEGER PRIMARY KEY AUTOINCREMENT,
    Date TEXT NOT NULL,
    Cell TEXT NOT NULL,
    MachineNumber TEXT NOT NULL,
    MachineName TEXT,
    RequestCategory TEXT,
    RequestType TEXT,
    Priority TEXT,
    MachineStatus TEXT,        -- Idle / Working
    ReasonForInspection TEXT,
    MachineIncharge TEXT,
    Stage2FlagRequested TEXT,  -- Yes/No, requester's initial guess
    Status TEXT DEFAULT 'Open' -- Open / In Progress / Closed
);

CREATE TABLE InspectionStage1 (
    InspectionID INTEGER PRIMARY KEY AUTOINCREMENT,
    RequestID INTEGER NOT NULL,
    StartDate TEXT,
    EndDate TEXT,
    Status TEXT,        -- Pass / Fail
    InspectedBy TEXT,
    Remarks TEXT,
    Stage2Required TEXT, -- Yes/No, inspector's confirmed call
    FOREIGN KEY (RequestID) REFERENCES Requests(RequestID)
);

CREATE TABLE InspectionStage2 (
    Stage2ID INTEGER PRIMARY KEY AUTOINCREMENT,
    InspectionID INTEGER NOT NULL,
    StartDate TEXT,
    EndDate TEXT,
    Status TEXT,
    InspectedBy TEXT,
    Remarks TEXT,
    FOREIGN KEY (InspectionID) REFERENCES InspectionStage1(InspectionID)
);
