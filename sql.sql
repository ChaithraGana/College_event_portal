SHOW DATABASES;
USE railway;

-- 1. Schools & Engineering Branches
CREATE TABLE Schools_Branches (
    sb_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    parent_id INT DEFAULT NULL, -- NULL for Schools; Links to 'School of Engineering' for branches
    is_school BOOLEAN DEFAULT TRUE, -- Schools (True), Branches (False)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES Schools_Branches(sb_id) ON DELETE CASCADE
) ENGINE=InnoDB;
SELECT * FROM Schools_Branches;
DROP TABLE Venues;
-- 2. Venues
CREATE TABLE Venues (
    venue_id INT AUTO_INCREMENT PRIMARY KEY,
    venue_name VARCHAR(100) NOT NULL,
    building_block VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


-- 3. Main Events (e.g., "Samyuthi")
-- Organizing Logic: Specific School ID or NULL for "University as a whole" [cite: 17]
CREATE TABLE Main_Events (
    main_event_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    organizing_school_id INT DEFAULT NULL, 
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organizing_school_id) REFERENCES Schools_Branches(sb_id)
) ENGINE=InnoDB;
truncate TABLE Main_Events;

-- 4. Sub-Events (The Activities)
-- Handles flexible event types (Section 2.1) 
CREATE TABLE Sub_Events (
    sub_event_id INT AUTO_INCREMENT PRIMARY KEY,
    main_event_id INT NOT NULL,
    sub_event_name VARCHAR(255) NOT NULL,
    category ENUM('technical', 'cultural', 'sports', 'workshop', 'other') NOT NULL, 
    venue_id INT NOT NULL,
    event_time DATETIME NOT NULL,
    organizing_school_id INT DEFAULT NULL, -- Specific school organizing this sub-event
    is_competition BOOLEAN DEFAULT FALSE, -- FALSE for workshops, TRUE for hackathons 
    description TEXT,
    FOREIGN KEY (main_event_id) REFERENCES Main_Events(main_event_id) ON DELETE CASCADE,
    FOREIGN KEY (organizing_school_id) REFERENCES Schools_Branches(sb_id),
    FOREIGN KEY (venue_id) REFERENCES Venues(venue_id)
) ENGINE=InnoDB;
SELECT * FROM Main_Events;
INSERT INTO Main_Events VALUES
(2, 'Cultural Fest', NULL, '2026-03-10', '2026-03-12',now()),
(3, 'Sports Day', NULL, '2026-03-10', '2026-03-12',now());


INSERT INTO Sub_Events (
    sub_event_id, main_event_id, sub_event_name, category, 
    venue_id, event_time, organizing_school_id, is_competition, description
) VALUES
(1, 1, 'Hackathon', 'technical', 2, '2026-03-11 10:00:00', 1, 1, 'Exciting Hackathon session.'),
(2, 1, 'Web Development', 'technical', 1, '2026-03-11 10:00:00', 1, 1, 'Exciting Web Development session.'),
(3, 1, 'Prompt to Product', 'technical', 4, '2026-03-11 10:00:00', 1, 1, 'Exciting Prompt to Product session.'),
(4, 1, 'Circuit Verse', 'technical', 4, '2026-03-11 10:00:00', 1, 1, 'Exciting Circuit Verse session.'),
(5, 1, 'RoboRush', 'technical', 4, '2026-03-11 10:00:00', 1, 1, 'Exciting RoboRush session.'),
(6, 2, 'IKS Online Hackathon', 'cultural', 2, '2026-03-11 10:00:00', NULL, 1, 'Exciting IKS Online Hackathon session.'),
(7, 2, 'Treasure Hunt', 'cultural', 5, '2026-03-11 10:00:00', NULL, 1, 'Exciting Treasure Hunt session.'),
(8, 2, 'Vastra Verse', 'cultural', 1, '2026-03-11 10:00:00', NULL, 1, 'Exciting Vastra Verse session.'),
(9, 2, 'Hardware Hackathon', 'cultural', 2, '2026-03-11 10:00:00', NULL, 1, 'Exciting Hardware Hackathon session.'),
(10, 2, 'Esports', 'cultural', 5, '2026-03-11 10:00:00', NULL, 1, 'Exciting Esports session.'),
(11, 3, 'Football', 'sports', 1, '2026-03-11 10:00:00', NULL, 1, 'Exciting Football session.'),
(12, 3, 'Throwball', 'sports', 3, '2026-03-11 10:00:00', NULL, 1, 'Exciting Throwball session.'),
(13, 3, 'Cricket', 'sports', 2, '2026-03-11 10:00:00', NULL, 1, 'Exciting Cricket session.'),
(14, 3, 'Table Tennis', 'sports', 4, '2026-03-11 10:00:00', NULL, 1, 'Exciting Table Tennis session.'),
(15, 3, 'Volleyball', 'sports', 4, '2026-03-11 10:00:00', NULL, 1, 'Exciting Volleyball session.'),
(16, 4, 'Hands-on Neural Networks', 'workshop', 1, '2026-03-11 10:00:00', 1, 0, 'Exciting Hands-on Neural Networks session.');

-- 5. Participants (Master Data)
CREATE TABLE Participants (
    participant_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_number VARCHAR(20) UNIQUE NOT NULL, 
    full_name VARCHAR(150) NOT NULL, 
    sb_id INT NOT NULL, -- Student's Branch/School 
    year_of_study TINYINT CHECK (year_of_study BETWEEN 1 AND 4), 
    is_internal BOOLEAN DEFAULT TRUE, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sb_id) REFERENCES Schools_Branches(sb_id)
) ENGINE=InnoDB;
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE Participants;

SET FOREIGN_KEY_CHECKS = 1;
INSERT INTO Participants (participant_id, roll_number, full_name, sb_id, year_of_study, is_internal) VALUES
(1, '2026BT001', 'Student 1', 2, 4, 1),
(2, '2026BT002', 'Student 2', 11, 1, 1),
(3, '2026BT003', 'Student 3', 11, 4, 1),
(4, '2026BT004', 'Student 4', 6, 1, 1),
(5, '2026BT005', 'Student 5', 10, 3, 1),
(6, '2026BT006', 'Student 6', 12, 3, 1),
(7, '2026BT007', 'Student 7', 7, 1, 1),
(8, '2026BT008', 'Student 8', 6, 2, 1),
(9, '2026BT009', 'Student 9', 12, 1, 1),
(10, '2026BT010', 'Student 10', 6, 3, 1),
(11, '2026BT011', 'Student 11', 5, 1, 1),
(12, '2026BT012', 'Student 12', 8, 4, 1),
(13, '2026BT013', 'Student 13', 7, 4, 1),
(14, '2026BT014', 'Student 14', 12, 3, 1),
(15, '2026BT015', 'Student 15', 12, 2, 1),
(16, '2026BT016', 'Student 16', 7, 2, 1),
(17, '2026BT017', 'Student 17', 7, 1, 1),
(18, '2026BT018', 'Student 18', 3, 1, 1),
(19, '2026BT019', 'Student 19', 6, 2, 1),
(20, '2026BT020', 'Student 20', 6, 2, 1),
(21, '2026BT021', 'Student 21', 1, 2, 1),
(22, '2026BT022', 'Student 22', 9, 3, 1),
(23, '2026BT023', 'Student 23', 7, 3, 1),
(24, '2026BT024', 'Student 24', 1, 4, 1),
(25, '2026BT025', 'Student 25', 2, 3, 1),
(26, '2026BT026', 'Student 26', 2, 1, 1),
(27, '2026BT027', 'Student 27', 1, 4, 1),
(28, '2026BT028', 'Student 28', 3, 1, 1),
(29, '2026BT029', 'Student 29', 10, 3, 1),
(30, '2026BT030', 'Student 30', 7, 1, 1),
(31, '2026BT031', 'Student 31', 6, 1, 1),
(32, '2026BT032', 'Student 32', 7, 4, 1),
(33, '2026BT033', 'Student 33', 10, 4, 1),
(34, '2026BT034', 'Student 34', 10, 2, 1),
(35, '2026BT035', 'Student 35', 8, 3, 1),
(36, '2026BT036', 'Student 36', 8, 1, 1),
(37, '2026BT037', 'Student 37', 2, 1, 1),
(38, '2026BT038', 'Student 38', 2, 4, 1),
(39, '2026BT039', 'Student 39', 9, 3, 1),
(40, '2026BT040', 'Student 40', 6, 2, 1),
(41, '2026BT041', 'Student 41', 11, 3, 1),
(42, '2026BT042', 'Student 42', 8, 2, 1),
(43, '2026BT043', 'Student 43', 4, 2, 1),
(44, '2026BT044', 'Student 44', 8, 3, 1),
(45, '2026BT045', 'Student 45', 4, 3, 1),
(46, '2026BT046', 'Student 46', 11, 4, 1),
(47, '2026BT047', 'Student 47', 2, 1, 1),
(48, '2026BT048', 'Student 48', 5, 1, 1),
(49, '2026BT049', 'Student 49', 5, 1, 1),
(50, '2026BT050', 'Student 50', 4, 3, 1),
(51, '2026BT051', 'Student 51', 5, 3, 1),
(52, '2026BT052', 'Student 52', 5, 1, 1),
(53, '2026BT053', 'Student 53', 3, 3, 1),
(54, '2026BT054', 'Student 54', 9, 4, 1),
(55, '2026BT055', 'Student 55', 10, 3, 1),
(56, '2026BT056', 'Student 56', 9, 1, 1),
(57, '2026BT057', 'Student 57', 3, 4, 1),
(58, '2026BT058', 'Student 58', 11, 1, 1),
(59, '2026BT059', 'Student 59', 1, 3, 1),
(60, '2026BT060', 'Student 60', 6, 1, 1),
(61, '2026BT061', 'Student 61', 4, 2, 1),
(62, '2026BT062', 'Student 62', 5, 3, 1),
(63, '2026BT063', 'Student 63', 7, 4, 1),
(64, '2026BT064', 'Student 64', 8, 4, 1),
(65, '2026BT065', 'Student 65', 8, 4, 1),
(66, '2026BT066', 'Student 66', 12, 2, 1),
(67, '2026BT067', 'Student 67', 8, 4, 1),
(68, '2026BT068', 'Student 68', 2, 3, 1),
(69, '2026BT069', 'Student 69', 9, 4, 1),
(70, '2026BT070', 'Student 70', 5, 3, 1),
(71, '2026BT071', 'Student 71', 7, 2, 1),
(72, '2026BT072', 'Student 72', 5, 2, 1),
(73, '2026BT073', 'Student 73', 10, 2, 1),
(74, '2026BT074', 'Student 74', 2, 1, 1),
(75, '2026BT075', 'Student 75', 7, 1, 1),
(76, '2026BT076', 'Student 76', 9, 4, 1),
(77, '2026BT077', 'Student 77', 2, 3, 1),
(78, '2026BT078', 'Student 78', 7, 4, 1),
(79, '2026BT079', 'Student 79', 2, 2, 1),
(80, '2026BT080', 'Student 80', 10, 3, 1),
(81, '2026BT081', 'Student 81', 10, 4, 1),
(82, '2026BT082', 'Student 82', 7, 1, 1),
(83, '2026BT083', 'Student 83', 7, 2, 1),
(84, '2026BT084', 'Student 84', 1, 1, 1),
(85, '2026BT085', 'Student 85', 4, 1, 1),
(86, '2026BT086', 'Student 86', 6, 1, 1),
(87, '2026BT087', 'Student 87', 5, 2, 1),
(88, '2026BT088', 'Student 88', 6, 1, 1),
(89, '2026BT089', 'Student 89', 10, 1, 1),
(90, '2026BT090', 'Student 90', 12, 3, 1),
(91, '2026BT091', 'Student 91', 9, 2, 1),
(92, '2026BT092', 'Student 92', 2, 3, 1),
(93, '2026BT093', 'Student 93', 11, 4, 1),
(94, '2026BT094', 'Student 94', 9, 4, 1),
(95, '2026BT095', 'Student 95', 2, 1, 1),
(96, '2026BT096', 'Student 96', 5, 3, 1),
(97, '2026BT097', 'Student 97', 11, 4, 1),
(98, '2026BT098', 'Student 98', 9, 3, 1),
(99, '2026BT099', 'Student 99', 10, 4, 1),
(100, '2026BT100', 'Student 100', 10, 2, 1);

-- 6. Event_Registrations (The "Raw Data" Link)
-- Every record gets a timestamp (Section 2.2) [cite: 27]
CREATE TABLE Event_Registrations (
    registration_id INT AUTO_INCREMENT PRIMARY KEY,
    sub_event_id INT NOT NULL,
    participant_id INT NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (sub_event_id) REFERENCES Sub_Events(sub_event_id) ON DELETE CASCADE,
    FOREIGN KEY (participant_id) REFERENCES Participants(participant_id) ON DELETE CASCADE,
    UNIQUE(sub_event_id, participant_id) 
) ENGINE=InnoDB;
-- This removes all existing data and resets the ID counter
TRUNCATE TABLE Event_Registrations;

INSERT INTO Event_Registrations (registration_id, sub_event_id, participant_id, registration_date) VALUES
(1, 2, 1, '2026-04-29 13:40:29'),
(2, 4, 1, '2026-04-29 13:40:29'),
(3, 16, 2, '2026-04-29 13:40:29'),
(4, 2, 2, '2026-04-29 13:40:29'),
(5, 5, 3, '2026-04-29 13:40:29'),
(6, 9, 3, '2026-04-29 13:40:29'),
(7, 7, 4, '2026-04-29 13:40:29'),
(8, 1, 4, '2026-04-29 13:40:29'),
(9, 8, 5, '2026-04-29 13:40:29'),
(10, 10, 5, '2026-04-29 13:40:29'),
(11, 3, 6, '2026-04-29 13:40:29'),
(12, 8, 6, '2026-04-29 13:40:29'),
(13, 4, 7, '2026-04-29 13:40:29'),
(14, 10, 7, '2026-04-29 13:40:29'),
(15, 9, 8, '2026-04-29 13:40:29'),
(16, 15, 8, '2026-04-29 13:40:29'),
(17, 10, 9, '2026-04-29 13:40:29'),
(18, 4, 9, '2026-04-29 13:40:29'),
(19, 7, 10, '2026-04-29 13:40:29'),
(20, 10, 10, '2026-04-29 13:40:29'),
(21, 10, 11, '2026-04-29 13:40:29'),
(22, 16, 11, '2026-04-29 13:40:29'),
(23, 14, 12, '2026-04-29 13:40:29'),
(24, 8, 12, '2026-04-29 13:40:29'),
(25, 1, 13, '2026-04-29 13:40:29'),
(26, 8, 13, '2026-04-29 13:40:29'),
(27, 7, 14, '2026-04-29 13:40:29'),
(28, 16, 14, '2026-04-29 13:40:29'),
(29, 13, 15, '2026-04-29 13:40:29'),
(30, 6, 15, '2026-04-29 13:40:29'),
(31, 6, 16, '2026-04-29 13:40:29'),
(32, 7, 16, '2026-04-29 13:40:29'),
(33, 5, 17, '2026-04-29 13:40:29'),
(34, 11, 17, '2026-04-29 13:40:29'),
(35, 6, 18, '2026-04-29 13:40:29'),
(36, 3, 18, '2026-04-29 13:40:29'),
(37, 1, 19, '2026-04-29 13:40:29'),
(38, 6, 19, '2026-04-29 13:40:29'),
(39, 7, 20, '2026-04-29 13:40:29'),
(40, 9, 20, '2026-04-29 13:40:29'),
(41, 11, 21, '2026-04-29 13:40:29'),
(42, 15, 21, '2026-04-29 13:40:29'),
(43, 4, 22, '2026-04-29 13:40:29'),
(44, 11, 22, '2026-04-29 13:40:29'),
(45, 10, 23, '2026-04-29 13:40:29'),
(46, 12, 23, '2026-04-29 13:40:29'),
(47, 12, 24, '2026-04-29 13:40:29'),
(48, 2, 24, '2026-04-29 13:40:29'),
(49, 14, 25, '2026-04-29 13:40:29'),
(50, 10, 25, '2026-04-29 13:40:29'),
(51, 8, 26, '2026-04-29 13:40:29'),
(52, 11, 26, '2026-04-29 13:40:29'),
(53, 14, 27, '2026-04-29 13:40:29'),
(54, 6, 27, '2026-04-29 13:40:29'),
(55, 15, 28, '2026-04-29 13:40:29'),
(56, 3, 28, '2026-04-29 13:40:29'),
(57, 10, 29, '2026-04-29 13:40:29'),
(58, 12, 29, '2026-04-29 13:40:29'),
(59, 7, 30, '2026-04-29 13:40:29'),
(60, 10, 30, '2026-04-29 13:40:29'),
(61, 2, 31, '2026-04-29 13:40:29'),
(62, 12, 31, '2026-04-29 13:40:29'),
(63, 12, 32, '2026-04-29 13:40:29'),
(64, 1, 32, '2026-04-29 13:40:29'),
(65, 16, 33, '2026-04-29 13:40:29'),
(66, 8, 33, '2026-04-29 13:40:29'),
(67, 2, 34, '2026-04-29 13:40:29'),
(68, 13, 34, '2026-04-29 13:40:29'),
(69, 9, 35, '2026-04-29 13:40:29'),
(70, 11, 35, '2026-04-29 13:40:29'),
(71, 3, 36, '2026-04-29 13:40:29'),
(72, 14, 36, '2026-04-29 13:40:29'),
(73, 8, 37, '2026-04-29 13:40:29'),
(74, 9, 37, '2026-04-29 13:40:29'),
(75, 12, 38, '2026-04-29 13:40:29'),
(76, 8, 38, '2026-04-29 13:40:29'),
(77, 11, 39, '2026-04-29 13:40:29'),
(78, 14, 39, '2026-04-29 13:40:29'),
(79, 14, 40, '2026-04-29 13:40:29'),
(80, 11, 40, '2026-04-29 13:40:29'),
(81, 9, 41, '2026-04-29 13:40:29'),
(82, 3, 41, '2026-04-29 13:40:29'),
(83, 3, 42, '2026-04-29 13:40:29'),
(84, 7, 42, '2026-04-29 13:40:29'),
(85, 11, 43, '2026-04-29 13:40:29'),
(86, 8, 43, '2026-04-29 13:40:29'),
(87, 15, 44, '2026-04-29 13:40:29'),
(88, 8, 44, '2026-04-29 13:40:29'),
(89, 7, 45, '2026-04-29 13:40:29'),
(90, 13, 45, '2026-04-29 13:40:29'),
(91, 6, 46, '2026-04-29 13:40:29'),
(92, 16, 46, '2026-04-29 13:40:29'),
(93, 14, 47, '2026-04-29 13:40:29'),
(94, 8, 47, '2026-04-29 13:40:29'),
(95, 3, 48, '2026-04-29 13:40:29'),
(96, 7, 48, '2026-04-29 13:40:29'),
(97, 11, 49, '2026-04-29 13:40:29'),
(98, 6, 49, '2026-04-29 13:40:29'),
(99, 14, 50, '2026-04-29 13:40:29'),
(100, 5, 50, '2026-04-29 13:40:29'),
(101, 9, 51, '2026-04-29 13:40:29'),
(102, 15, 51, '2026-04-29 13:40:29'),
(103, 15, 52, '2026-04-29 13:40:29'),
(104, 8, 52, '2026-04-29 13:40:29'),
(105, 13, 53, '2026-04-29 13:40:29'),
(106, 4, 53, '2026-04-29 13:40:29'),
(107, 15, 54, '2026-04-29 13:40:29'),
(108, 9, 54, '2026-04-29 13:40:29'),
(109, 8, 55, '2026-04-29 13:40:29'),
(110, 16, 55, '2026-04-29 13:40:29'),
(111, 9, 56, '2026-04-29 13:40:29'),
(112, 3, 56, '2026-04-29 13:40:29'),
(113, 14, 57, '2026-04-29 13:40:29'),
(114, 15, 57, '2026-04-29 13:40:29'),
(115, 3, 58, '2026-04-29 13:40:29'),
(116, 11, 58, '2026-04-29 13:40:29'),
(117, 12, 59, '2026-04-29 13:40:29'),
(118, 15, 59, '2026-04-29 13:40:29'),
(119, 9, 60, '2026-04-29 13:40:29'),
(120, 2, 60, '2026-04-29 13:40:29'),
(121, 5, 61, '2026-04-29 13:40:29'),
(122, 10, 61, '2026-04-29 13:40:29'),
(123, 7, 62, '2026-04-29 13:40:29'),
(124, 11, 62, '2026-04-29 13:40:29'),
(125, 1, 63, '2026-04-29 13:40:29'),
(126, 10, 63, '2026-04-29 13:40:29'),
(127, 2, 64, '2026-04-29 13:40:29'),
(128, 7, 64, '2026-04-29 13:40:29'),
(129, 9, 65, '2026-04-29 13:40:29'),
(130, 4, 65, '2026-04-29 13:40:29'),
(131, 1, 66, '2026-04-29 13:40:29'),
(132, 9, 66, '2026-04-29 13:40:29'),
(133, 8, 67, '2026-04-29 13:40:29'),
(134, 6, 67, '2026-04-29 13:40:29'),
(135, 8, 68, '2026-04-29 13:40:29'),
(136, 13, 68, '2026-04-29 13:40:29'),
(137, 7, 69, '2026-04-29 13:40:29'),
(138, 10, 69, '2026-04-29 13:40:29'),
(139, 14, 70, '2026-04-29 13:40:29'),
(140, 7, 70, '2026-04-29 13:40:29'),
(141, 3, 71, '2026-04-29 13:40:29'),
(142, 11, 71, '2026-04-29 13:40:29'),
(143, 16, 72, '2026-04-29 13:40:29'),
(144, 4, 72, '2026-04-29 13:40:29'),
(145, 13, 73, '2026-04-29 13:40:29'),
(146, 5, 73, '2026-04-29 13:40:29'),
(147, 7, 74, '2026-04-29 13:40:29'),
(148, 10, 74, '2026-04-29 13:40:29'),
(149, 3, 75, '2026-04-29 13:40:29'),
(150, 8, 75, '2026-04-29 13:40:29'),
(151, 14, 76, '2026-04-29 13:40:29'),
(152, 15, 76, '2026-04-29 13:40:29'),
(153, 5, 77, '2026-04-29 13:40:29'),
(154, 14, 77, '2026-04-29 13:40:29'),
(155, 9, 78, '2026-04-29 13:40:29'),
(156, 5, 78, '2026-04-29 13:40:29'),
(157, 11, 79, '2026-04-29 13:40:29'),
(158, 9, 79, '2026-04-29 13:40:29'),
(159, 9, 80, '2026-04-29 13:40:29'),
(160, 7, 80, '2026-04-29 13:40:29'),
(161, 9, 81, '2026-04-29 13:40:29'),
(162, 8, 81, '2026-04-29 13:40:29'),
(163, 12, 82, '2026-04-29 13:40:29'),
(164, 4, 82, '2026-04-29 13:40:29'),
(165, 7, 83, '2026-04-29 13:40:29'),
(166, 11, 83, '2026-04-29 13:40:29'),
(167, 4, 84, '2026-04-29 13:40:29'),
(168, 11, 84, '2026-04-29 13:40:29'),
(169, 2, 85, '2026-04-29 13:40:29'),
(170, 7, 85, '2026-04-29 13:40:29'),
(171, 14, 86, '2026-04-29 13:40:29'),
(172, 9, 86, '2026-04-29 13:40:29'),
(173, 6, 87, '2026-04-29 13:40:29'),
(174, 4, 87, '2026-04-29 13:40:29'),
(175, 16, 88, '2026-04-29 13:40:29'),
(176, 7, 88, '2026-04-29 13:40:29'),
(177, 2, 89, '2026-04-29 13:40:29'),
(178, 16, 89, '2026-04-29 13:40:29'),
(179, 1, 90, '2026-04-29 13:40:29'),
(180, 8, 90, '2026-04-29 13:40:29'),
(181, 9, 91, '2026-04-29 13:40:29'),
(182, 5, 91, '2026-04-29 13:40:29'),
(183, 16, 92, '2026-04-29 13:40:29'),
(184, 4, 92, '2026-04-29 13:40:29'),
(185, 7, 93, '2026-04-29 13:40:29'),
(186, 6, 93, '2026-04-29 13:40:29'),
(187, 9, 94, '2026-04-29 13:40:29'),
(188, 1, 94, '2026-04-29 13:40:29'),
(189, 8, 95, '2026-04-29 13:40:29'),
(190, 2, 95, '2026-04-29 13:40:29'),
(191, 16, 96, '2026-04-29 13:40:29'),
(192, 1, 96, '2026-04-29 13:40:29'),
(193, 7, 97, '2026-04-29 13:40:29'),
(194, 3, 97, '2026-04-29 13:40:29'),
(195, 9, 98, '2026-04-29 13:40:29'),
(196, 14, 98, '2026-04-29 13:40:29'),
(197, 3, 99, '2026-04-29 13:40:29'),
(198, 7, 99, '2026-04-29 13:40:29'),
(199, 6, 100, '2026-04-29 13:40:29'),
(200, 1, 100, '2026-04-29 13:40:29');

-- 7. Competition_Results (Optional Winner Data)
-- This table ONLY contains rows for competitive events where winners are declared.
-- Workshops will simply never have a corresponding row here. [cite: 20, 21]
CREATE TABLE Competition_Results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    sub_event_id INT NOT NULL,
    participant_id INT NOT NULL, -- The winner
    rank_position INT NOT NULL, -- e.g., 1, 2, 3 [cite: 19]
    award_prize VARCHAR(255), 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (sub_event_id) REFERENCES Sub_Events(sub_event_id) ON DELETE CASCADE,
    FOREIGN KEY (participant_id) REFERENCES Participants(participant_id) ON DELETE CASCADE
) ENGINE=InnoDB;
SELECT * FROM Competition_Results;

-- Total participants per main event
SELECT 
    me.title,
    COUNT(er.registration_id) AS total_participants
FROM Main_Events me
JOIN Sub_Events se ON me.main_event_id = se.main_event_id
JOIN Event_Registrations er ON se.sub_event_id = er.sub_event_id
GROUP BY me.main_event_id
ORDER BY total_participants DESC;

-- Most popular Sub-event
SELECT 
    se.sub_event_name,
    COUNT(er.participant_id) AS participants_count
FROM Sub_Events se
LEFT JOIN Event_Registrations er ON se.sub_event_id = er.sub_event_id
GROUP BY se.sub_event_id
ORDER BY participants_count DESC
LIMIT 5;

-- Events Organised by each School
SELECT 
    sb.name AS organizing_school,
    COUNT(se.sub_event_id) AS total_events
FROM Schools_Branches sb
JOIN Sub_Events se ON sb.sb_id = se.organizing_school_id
GROUP BY sb.sb_id
ORDER BY total_events DESC;

-- Winner count by school
SELECT 
    sb.name AS school_branch,
    COUNT(cr.result_id) AS total_wins
FROM Competition_Results cr
JOIN Participants p ON cr.participant_id = p.participant_id
JOIN Schools_Branches sb ON p.sb_id = sb.sb_id
GROUP BY sb.sb_id
ORDER BY total_wins DESC;

-- Category wise event Distribution
SELECT 
    category,
    COUNT(*) AS total_events
FROM Sub_Events
GROUP BY category;

-- Top 3 Participants with most registrations
SELECT 
    p.full_name,
    COUNT(er.sub_event_id) AS events_participated
FROM Participants p
JOIN Event_Registrations er ON p.participant_id = er.participant_id
GROUP BY p.participant_id
ORDER BY events_participated DESC
LIMIT 3;

-- Average participation per event
SELECT 
    AVG(participant_count) AS avg_participation
FROM (
    SELECT 
        se.sub_event_id,
        COUNT(er.participant_id) AS participant_count
    FROM Sub_Events se
    LEFT JOIN Event_Registrations er 
        ON se.sub_event_id = er.sub_event_id
    GROUP BY se.sub_event_id
) AS event_stats;

-- Students Winning atleast two events
SELECT 
    p.full_name,
    p.roll_number,
    COUNT(cr.sub_event_id) AS total_wins
FROM Competition_Results cr
JOIN Participants p 
    ON cr.participant_id = p.participant_id
GROUP BY p.participant_id
HAVING COUNT(cr.sub_event_id) >= 2
ORDER BY total_wins DESC;

