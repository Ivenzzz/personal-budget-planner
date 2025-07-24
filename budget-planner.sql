-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jul 24, 2025 at 02:36 AM
-- Server version: 8.4.3
-- PHP Version: 8.3.16

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `budget-planner`
--

-- --------------------------------------------------------

--
-- Table structure for table `budgets`
--

CREATE TABLE `budgets` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `category_id` int NOT NULL,
  `budget_amount` decimal(10,2) NOT NULL,
  `month` tinyint NOT NULL,
  `year` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `budgets`
--

INSERT INTO `budgets` (`id`, `user_id`, `category_id`, `budget_amount`, `month`, `year`, `created_at`) VALUES
(1, 1, 6, 600.00, 7, 2025, '2025-07-24 02:09:07'),
(2, 1, 7, 900.00, 7, 2025, '2025-07-24 02:09:07'),
(3, 1, 12, 100.00, 7, 2025, '2025-07-24 02:09:07'),
(4, 1, 13, 40.00, 7, 2025, '2025-07-24 02:09:07'),
(5, 1, 14, 70.00, 7, 2025, '2025-07-24 02:09:07');

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

CREATE TABLE `categories` (
  `id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `name` varchar(50) NOT NULL,
  `type` enum('income','expense') NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`id`, `user_id`, `name`, `type`, `created_at`) VALUES
(1, NULL, 'Salary', 'income', '2025-07-24 02:03:32'),
(2, NULL, 'Freelancing', 'income', '2025-07-24 02:03:32'),
(3, NULL, 'Investment Returns', 'income', '2025-07-24 02:03:32'),
(4, NULL, 'Gift', 'income', '2025-07-24 02:03:32'),
(5, NULL, 'Other Income', 'income', '2025-07-24 02:03:32'),
(6, NULL, 'Groceries', 'expense', '2025-07-24 02:03:32'),
(7, NULL, 'Rent', 'expense', '2025-07-24 02:03:32'),
(8, NULL, 'Utilities', 'expense', '2025-07-24 02:03:32'),
(9, NULL, 'Transportation', 'expense', '2025-07-24 02:03:32'),
(10, NULL, 'Entertainment', 'expense', '2025-07-24 02:03:32'),
(11, NULL, 'Food & Dining', 'expense', '2025-07-24 02:03:32'),
(12, NULL, 'Electricity Bill', 'expense', '2025-07-24 02:03:32'),
(13, NULL, 'Water Bill', 'expense', '2025-07-24 02:03:32'),
(14, NULL, 'Internet & Phone', 'expense', '2025-07-24 02:03:32'),
(15, NULL, 'Healthcare', 'expense', '2025-07-24 02:03:32');

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `category_id` int NOT NULL,
  `type` enum('income','expense') NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `description` text,
  `transaction_date` date NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `transactions`
--

INSERT INTO `transactions` (`id`, `user_id`, `category_id`, `type`, `amount`, `description`, `transaction_date`, `created_at`) VALUES
(1, 1, 1, 'income', 3000.00, 'Monthly salary for July', '2025-07-01', '2025-07-24 02:07:17'),
(2, 3, 2, 'income', 800.00, 'Freelance web design project', '2025-07-10', '2025-07-24 02:07:17'),
(3, 2, 6, 'expense', 150.50, 'Weekly groceries', '2025-07-05', '2025-07-24 02:07:17'),
(4, 1, 7, 'expense', 900.00, 'Monthly rent payment', '2025-07-01', '2025-07-24 02:07:17'),
(5, 1, 12, 'expense', 75.00, 'Electricity bill', '2025-07-08', '2025-07-24 02:07:17'),
(6, 3, 13, 'expense', 30.00, 'Water bill', '2025-07-08', '2025-07-24 02:07:17'),
(7, 2, 10, 'expense', 60.00, 'Movie and dinner with friends', '2025-07-15', '2025-07-24 02:07:17'),
(8, 1, 14, 'expense', 55.00, 'Internet and phone plan', '2025-07-03', '2025-07-24 02:07:17'),
(9, 3, 11, 'expense', 120.00, 'Dining out with family', '2025-07-12', '2025-07-24 02:07:17'),
(10, 3, 3, 'income', 200.00, 'Dividend payout', '2025-07-18', '2025-07-24 02:07:17');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `type` enum('user','admin') NOT NULL DEFAULT 'user',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `type`, `created_at`) VALUES
(1, 'alice', '$2a$12$0RBhu8IWwpwzjGOH89qQ1epYUoVoFKyLyjjCFfePC2nQ0UiBJPm1O', 'user', '2025-07-24 01:57:04'),
(2, 'bob', '$2a$12$0RBhu8IWwpwzjGOH89qQ1epYUoVoFKyLyjjCFfePC2nQ0UiBJPm1O', 'user', '2025-07-24 01:57:04'),
(3, 'charlie', '$2a$12$0RBhu8IWwpwzjGOH89qQ1epYUoVoFKyLyjjCFfePC2nQ0UiBJPm1O', 'user', '2025-07-24 01:57:04'),
(4, 'diana', '$2a$12$0RBhu8IWwpwzjGOH89qQ1epYUoVoFKyLyjjCFfePC2nQ0UiBJPm1O', 'user', '2025-07-24 01:57:04'),
(5, 'edward', '$2a$12$0RBhu8IWwpwzjGOH89qQ1epYUoVoFKyLyjjCFfePC2nQ0UiBJPm1O', 'user', '2025-07-24 01:57:04');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `budgets`
--
ALTER TABLE `budgets`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `budgets`
--
ALTER TABLE `budgets`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `categories`
--
ALTER TABLE `categories`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `budgets`
--
ALTER TABLE `budgets`
  ADD CONSTRAINT `budgets_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `budgets_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `categories`
--
ALTER TABLE `categories`
  ADD CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
