CREATE TABLE `academicYears` (
	`id` int AUTO_INCREMENT NOT NULL,
	`yearName` varchar(32) NOT NULL,
	`displayName` varchar(64),
	`status` enum('active','draft') NOT NULL DEFAULT 'draft',
	`isCurrentYear` tinyint DEFAULT 0,
	`studentSelectionStart` timestamp,
	`studentSelectionEnd` timestamp,
	`teacherConfirmStart` timestamp,
	`teacherConfirmEnd` timestamp,
	`maxWishesNormal` int DEFAULT 5,
	`maxWishesTransfer` int DEFAULT 8,
	`effectiveWishes` int DEFAULT 5,
	`statementRequired` tinyint DEFAULT 0,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	`chineseTeacherQuota` int DEFAULT 5,
	`thesisUploadStart` timestamp,
	`thesisUploadEnd` timestamp,
	`scoringStart` timestamp,
	`scoringEnd` timestamp,
	`transferStudentSelectionStart` timestamp,
	`transferStudentSelectionEnd` timestamp,
	CONSTRAINT `academicYears_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `adminLogs` (
	`id` int AUTO_INCREMENT NOT NULL,
	`adminId` int NOT NULL,
	`adminName` varchar(128),
	`action` varchar(64) NOT NULL,
	`module` varchar(64) NOT NULL,
	`targetType` varchar(64),
	`targetId` int,
	`targetName` varchar(256),
	`description` text,
	`beforeData` text,
	`afterData` text,
	`ipAddress` varchar(64),
	`userAgent` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `adminLogs_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `conflicts` (
	`id` int AUTO_INCREMENT NOT NULL,
	`topicId` int NOT NULL,
	`teacherId` int NOT NULL,
	`studentIds` json NOT NULL,
	`selectedStudentId` int,
	`matchRound` int DEFAULT 1,
	`deadline` timestamp,
	`resolved` tinyint DEFAULT 0,
	`academicYear` varchar(32),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `conflicts_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `guidanceAttachments` (
	`id` int AUTO_INCREMENT NOT NULL,
	`logId` int,
	`studentId` int NOT NULL,
	`fileName` varchar(256) NOT NULL,
	`fileUrl` varchar(1024) NOT NULL,
	`fileKey` varchar(512) NOT NULL,
	`mimeType` varchar(128),
	`fileSize` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `guidanceAttachments_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `guidanceComments` (
	`id` int AUTO_INCREMENT NOT NULL,
	`logId` int NOT NULL,
	`userId` int NOT NULL,
	`userRole` enum('student','teacher') NOT NULL,
	`content` text NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `guidanceComments_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `guidanceLogs` (
	`id` int AUTO_INCREMENT NOT NULL,
	`studentId` int NOT NULL,
	`teacherId` int NOT NULL,
	`guidanceDate` timestamp NOT NULL,
	`topic` varchar(256) NOT NULL,
	`content` text NOT NULL,
	`status` enum('draft','submitted','confirmed') NOT NULL DEFAULT 'draft',
	`academicYear` varchar(32),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `guidanceLogs_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `jointScores` (
	`id` int AUTO_INCREMENT NOT NULL,
	`matchId` int NOT NULL,
	`finalScore` int NOT NULL,
	`scoreMethod` enum('average','negotiated','majority') NOT NULL,
	`firstSupervisorId` int NOT NULL,
	`secondSupervisorId` int NOT NULL,
	`thirdSupervisorId` int,
	`jointComments` text,
	`confirmedBy` varchar(256),
	`confirmedAt` timestamp NOT NULL DEFAULT (now()),
	`academicYear` varchar(16),
	CONSTRAINT `jointScores_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `matches` (
	`id` int AUTO_INCREMENT NOT NULL,
	`studentId` int NOT NULL,
	`topicId` int NOT NULL,
	`teacherId` int NOT NULL,
	`secondTeacherId` int,
	`matchRound` int DEFAULT 1,
	`isAdjustment` tinyint DEFAULT 0,
	`academicYear` varchar(32),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`score` int,
	`remarks` text,
	CONSTRAINT `matches_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `purchaseRequests` (
	`id` int AUTO_INCREMENT NOT NULL,
	`studentId` int NOT NULL,
	`studentName` varchar(128) NOT NULL,
	`studentClass` varchar(64) NOT NULL,
	`studentNo` varchar(32) NOT NULL,
	`totalAmount` decimal(10,2) NOT NULL,
	`reason` text,
	`fileUrl` varchar(1024) NOT NULL,
	`fileKey` varchar(512) NOT NULL,
	`fileName` varchar(256) NOT NULL,
	`applyTime` timestamp NOT NULL DEFAULT (now()),
	`status` enum('pending_lab','pending_teacher','pending_asset','approved','rejected_lab','rejected_teacher','rejected_asset') NOT NULL DEFAULT 'pending_lab',
	`isOverBudget` tinyint DEFAULT 0,
	`labReviewedAt` timestamp,
	`labReviewedBy` int,
	`labComment` text,
	`teacherReviewedAt` timestamp,
	`teacherReviewedBy` int,
	`teacherComment` text,
	`assetReviewedAt` timestamp,
	`assetReviewedBy` int,
	`assetComment` text,
	`academicYear` varchar(32),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `purchaseRequests_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `scoringProgress` (
	`id` int AUTO_INCREMENT NOT NULL,
	`matchId` int NOT NULL,
	`status` enum('not_started','draft_uploaded','first_scored','second_assigned','second_scored','score_diff_small','score_diff_large','third_assigned','third_scored','completed') NOT NULL DEFAULT 'not_started',
	`scoreDifference` int,
	`needsThirdSupervisor` tinyint DEFAULT 0,
	`adminNotified` tinyint DEFAULT 0,
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	`academicYear` varchar(16),
	CONSTRAINT `scoringProgress_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `specialRoles` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int NOT NULL,
	`roleType` enum('lab_admin','asset_leader') NOT NULL,
	`appointedBy` int NOT NULL,
	`appointedAt` timestamp NOT NULL DEFAULT (now()),
	`status` enum('active','revoked') NOT NULL DEFAULT 'active',
	`revokedAt` timestamp,
	`wechatId` varchar(64),
	`wechatNote` text,
	CONSTRAINT `specialRoles_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `supervisorAssignments` (
	`id` int AUTO_INCREMENT NOT NULL,
	`matchId` int NOT NULL,
	`teacherId` int NOT NULL,
	`supervisorRole` enum('second','third') NOT NULL,
	`assignedBy` int,
	`assignmentMethod` enum('manual','random') DEFAULT 'manual',
	`status` enum('pending','accepted','completed') DEFAULT 'pending',
	`notifiedAt` timestamp,
	`assignedAt` timestamp NOT NULL DEFAULT (now()),
	`academicYear` varchar(16),
	CONSTRAINT `supervisorAssignments_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `systemConfig` (
	`id` int AUTO_INCREMENT NOT NULL,
	`configKey` varchar(64) NOT NULL,
	`configValue` text NOT NULL,
	`description` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `systemConfig_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `thesisDraftHistory` (
	`id` int AUTO_INCREMENT NOT NULL,
	`draftId` int NOT NULL,
	`studentId` int NOT NULL,
	`fileName` varchar(256) NOT NULL,
	`fileKey` varchar(512) NOT NULL,
	`fileUrl` varchar(1024) NOT NULL,
	`fileSize` int NOT NULL,
	`mimeType` varchar(128) NOT NULL,
	`version` int NOT NULL,
	`archivedAt` timestamp NOT NULL DEFAULT (now()),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `thesisDraftHistory_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `thesisDrafts` (
	`id` int AUTO_INCREMENT NOT NULL,
	`studentId` int NOT NULL,
	`matchId` int NOT NULL,
	`fileName` varchar(256) NOT NULL,
	`fileKey` varchar(512) NOT NULL,
	`fileUrl` varchar(1024) NOT NULL,
	`fileSize` int NOT NULL,
	`mimeType` varchar(128) NOT NULL,
	`version` int NOT NULL DEFAULT 1,
	`status` enum('submitted','reviewed','approved') NOT NULL DEFAULT 'submitted',
	`submittedAt` timestamp NOT NULL DEFAULT (now()),
	`academicYear` varchar(32),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	`score` int,
	`scoredAt` timestamp,
	`scoredBy` int,
	`secondTeacherScore` int,
	`secondTeacherScoredAt` timestamp,
	`secondTeacherScoredBy` int,
	`firstTeacherComment` text,
	`secondTeacherComment` text,
	`requestAverage` tinyint DEFAULT 0,
	`requestManualAdjust` tinyint DEFAULT 0,
	`requestReason` text,
	`rejectReason` text,
	`averageConfirmed` tinyint,
	`finalScore` decimal(4,1),
	`finalScoreConfirmedAt` timestamp,
	`lateSubmission` tinyint DEFAULT 0,
	`latePenalty` int DEFAULT 0,
	CONSTRAINT `thesisDrafts_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `thesisFinalDrafts` (
	`id` int AUTO_INCREMENT NOT NULL,
	`matchId` int NOT NULL,
	`studentId` int NOT NULL,
	`fileUrl` varchar(1024) NOT NULL,
	`fileKey` varchar(512) NOT NULL,
	`fileName` varchar(256) NOT NULL,
	`fileSize` int,
	`version` int DEFAULT 1,
	`uploadedAt` timestamp NOT NULL DEFAULT (now()),
	`academicYear` varchar(16),
	CONSTRAINT `thesisFinalDrafts_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `thesisScores` (
	`id` int AUTO_INCREMENT NOT NULL,
	`matchId` int NOT NULL,
	`draftId` int NOT NULL,
	`teacherId` int NOT NULL,
	`supervisorRole` enum('first','second','third') NOT NULL,
	`score` int NOT NULL,
	`comments` text,
	`scoredAt` timestamp NOT NULL DEFAULT (now()),
	`academicYear` varchar(16),
	CONSTRAINT `thesisScores_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `titleChangeRequests` (
	`id` int AUTO_INCREMENT NOT NULL,
	`matchId` int NOT NULL,
	`studentId` int NOT NULL,
	`teacherId` int NOT NULL,
	`originalTitle` varchar(512) NOT NULL,
	`newTitle` varchar(512) NOT NULL,
	`reason` text,
	`status` enum('pending','approved','rejected') NOT NULL DEFAULT 'pending',
	`reviewedAt` timestamp,
	`reviewComment` text,
	`academicYear` varchar(32),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `titleChangeRequests_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `topicLibrary` (
	`id` int AUTO_INCREMENT NOT NULL,
	`originalTopicId` int NOT NULL,
	`title` varchar(512) NOT NULL,
	`titleEn` varchar(512),
	`teacherId` int NOT NULL,
	`teacherName` varchar(128),
	`publishedAt` timestamp NOT NULL DEFAULT (now()),
	`status` enum('published','used','withdrawn') NOT NULL DEFAULT 'published',
	`academicYear` varchar(32),
	`description` text,
	`suitableFor` varchar(64),
	`topicSource` varchar(128),
	`researchProjectName` varchar(256),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `topicLibrary_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `topics` (
	`id` int AUTO_INCREMENT NOT NULL,
	`teacherId` int NOT NULL,
	`title` varchar(512) NOT NULL,
	`titleEn` varchar(512),
	`description` text NOT NULL,
	`descriptionEn` text,
	`requiredSkills` text,
	`suitableMajor` enum('electronic_info','communication','both') DEFAULT 'both',
	`status` enum('draft','published','used') NOT NULL DEFAULT 'draft',
	`isCurrentYear` tinyint DEFAULT 0,
	`academicYear` varchar(32),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	`keywords` varchar(512),
	`researchFocus` varchar(256),
	`thesisType` varchar(64) DEFAULT '毕业设计',
	`topicSource` varchar(64) DEFAULT '其他',
	`topicLanguage` varchar(16) DEFAULT '英语',
	`researchProjectName` varchar(256),
	`language` varchar(16) DEFAULT '英语',
	CONSTRAINT `topics_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `wishes` (
	`id` int AUTO_INCREMENT NOT NULL,
	`studentId` int NOT NULL,
	`topicId` int NOT NULL,
	`priority` int NOT NULL,
	`statement` text,
	`status` enum('pending','selected','rejected','matched') NOT NULL DEFAULT 'pending',
	`academicYear` varchar(32),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	`teacherDecision` enum('pending','approved','rejected') DEFAULT 'pending',
	`decisionAt` timestamp,
	`currentPriority` int DEFAULT 1,
	CONSTRAINT `wishes_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
ALTER TABLE `users` DROP INDEX `users_openId_unique`;--> statement-breakpoint
ALTER TABLE `users` MODIFY COLUMN `openId` varchar(64);--> statement-breakpoint
ALTER TABLE `users` MODIFY COLUMN `name` varchar(128);--> statement-breakpoint
ALTER TABLE `users` MODIFY COLUMN `email` varchar(320) NOT NULL;--> statement-breakpoint
ALTER TABLE `users` MODIFY COLUMN `role` enum('admin','teacher','student') NOT NULL DEFAULT 'student';--> statement-breakpoint
ALTER TABLE `users` MODIFY COLUMN `lastSignedIn` timestamp;--> statement-breakpoint
ALTER TABLE `users` ADD `password` varchar(256) NOT NULL;--> statement-breakpoint
ALTER TABLE `users` ADD `teacherType` enum('chinese','british');--> statement-breakpoint
ALTER TABLE `users` ADD `studentType` enum('transfer','non_transfer');--> statement-breakpoint
ALTER TABLE `users` ADD `studentMajor` enum('electronic_info','communication');--> statement-breakpoint
ALTER TABLE `users` ADD `annualQuota` int;--> statement-breakpoint
ALTER TABLE `users` ADD `language` enum('zh','en') DEFAULT 'zh';--> statement-breakpoint
ALTER TABLE `users` ADD `studentId` varchar(32);--> statement-breakpoint
ALTER TABLE `users` ADD `candidateNo` varchar(32);--> statement-breakpoint
ALTER TABLE `users` ADD `studentClass` varchar(64);--> statement-breakpoint
ALTER TABLE `users` ADD `faculty` varchar(128) DEFAULT '萨塞克斯人工智能学院';--> statement-breakpoint
ALTER TABLE `users` ADD `initialPassword` varchar(256) DEFAULT '123456';--> statement-breakpoint
ALTER TABLE `users` ADD `teacherNo` varchar(32) DEFAULT '0000000';--> statement-breakpoint
ALTER TABLE `users` ADD `sussexEmail` varchar(320);--> statement-breakpoint
ALTER TABLE `users` ADD `sussexId` varchar(32);--> statement-breakpoint
ALTER TABLE `users` ADD `academicYear` varchar(20);--> statement-breakpoint
ALTER TABLE `users` ADD `canPublish` tinyint DEFAULT 1;--> statement-breakpoint
ALTER TABLE `users` ADD `namePinyin` varchar(128);--> statement-breakpoint
CREATE INDEX `idx_adminId` ON `adminLogs` (`adminId`);--> statement-breakpoint
CREATE INDEX `idx_action` ON `adminLogs` (`action`);--> statement-breakpoint
CREATE INDEX `idx_module` ON `adminLogs` (`module`);--> statement-breakpoint
CREATE INDEX `idx_createdAt` ON `adminLogs` (`createdAt`);--> statement-breakpoint
CREATE INDEX `matchId` ON `jointScores` (`matchId`);--> statement-breakpoint
CREATE INDEX `idx_matches_studentId` ON `matches` (`studentId`);--> statement-breakpoint
CREATE INDEX `idx_matches_topicId` ON `matches` (`topicId`);--> statement-breakpoint
CREATE INDEX `idx_matches_teacherId` ON `matches` (`teacherId`);--> statement-breakpoint
CREATE INDEX `idx_matches_academicYear` ON `matches` (`academicYear`);--> statement-breakpoint
CREATE INDEX `idx_matches_student_year` ON `matches` (`studentId`,`academicYear`);--> statement-breakpoint
CREATE INDEX `idx_studentId` ON `purchaseRequests` (`studentId`);--> statement-breakpoint
CREATE INDEX `idx_status` ON `purchaseRequests` (`status`);--> statement-breakpoint
CREATE INDEX `matchId` ON `scoringProgress` (`matchId`);--> statement-breakpoint
CREATE INDEX `idx_draftId` ON `thesisDraftHistory` (`draftId`);--> statement-breakpoint
CREATE INDEX `idx_studentId` ON `thesisDraftHistory` (`studentId`);--> statement-breakpoint
CREATE INDEX `idx_studentId` ON `thesisDrafts` (`studentId`);--> statement-breakpoint
CREATE INDEX `idx_matchId` ON `thesisDrafts` (`matchId`);--> statement-breakpoint
CREATE INDEX `idx_academicYear` ON `thesisDrafts` (`academicYear`);--> statement-breakpoint
CREATE INDEX `matchId` ON `titleChangeRequests` (`matchId`);--> statement-breakpoint
CREATE INDEX `studentId` ON `titleChangeRequests` (`studentId`);--> statement-breakpoint
CREATE INDEX `teacherId` ON `titleChangeRequests` (`teacherId`);--> statement-breakpoint
CREATE INDEX `idx_wishes_studentId` ON `wishes` (`studentId`);--> statement-breakpoint
CREATE INDEX `idx_wishes_topicId` ON `wishes` (`topicId`);--> statement-breakpoint
CREATE INDEX `idx_wishes_academicYear` ON `wishes` (`academicYear`);--> statement-breakpoint
CREATE INDEX `idx_wishes_teacherDecision` ON `wishes` (`teacherDecision`);--> statement-breakpoint
CREATE INDEX `idx_wishes_composite` ON `wishes` (`academicYear`,`teacherDecision`,`topicId`);