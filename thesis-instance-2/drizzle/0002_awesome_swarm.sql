CREATE TABLE `userActivityLogs` (
	`id` int AUTO_INCREMENT NOT NULL,
	`userId` int NOT NULL,
	`userName` varchar(128),
	`userRole` varchar(32) NOT NULL,
	`action` varchar(64) NOT NULL,
	`module` varchar(64) NOT NULL,
	`targetType` varchar(64),
	`targetId` int,
	`targetName` varchar(256),
	`description` text,
	`result` varchar(16) DEFAULT 'success',
	`ipAddress` varchar(64),
	`userAgent` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `userActivityLogs_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE INDEX `idx_ual_userId` ON `userActivityLogs` (`userId`);--> statement-breakpoint
CREATE INDEX `idx_ual_userRole` ON `userActivityLogs` (`userRole`);--> statement-breakpoint
CREATE INDEX `idx_ual_action` ON `userActivityLogs` (`action`);--> statement-breakpoint
CREATE INDEX `idx_ual_module` ON `userActivityLogs` (`module`);--> statement-breakpoint
CREATE INDEX `idx_ual_createdAt` ON `userActivityLogs` (`createdAt`);