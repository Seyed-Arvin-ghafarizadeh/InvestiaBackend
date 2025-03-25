# InvestiaBackend
**Overview**
The Investia Telegram Bot is a Python-based application that enhances user onboarding and engagement for the Investia platform via Telegram. Leveraging the telegram.ext library, this bot collects user information (full name, phone, email, and optional comments), validates inputs with regex, and stores data securely in Google Firebase Firestore. After registration, users can select and receive links to Investia’s Forex, Crypto, or combined Telegram channels using an interactive inline keyboard. This project demonstrates robust error handling, real-time database integration, and a user-friendly interface, making it ideal for community management and data collection.

**Features**
User Data Collection: Gathers and validates full name (no digits), 11-digit phone number, and email with regex patterns.
Firebase Integration: Stores user data with timestamps in Firestore for persistence and analytics.
Channel Subscription: Offers inline keyboard options for Forex, Crypto, or both channels with direct Telegram links.
Input Validation: Ensures data integrity with checks for numeric-free names, valid phone lengths, and email formats.
Asynchronous Design: Built with telegram.ext for efficient, non-blocking message handling.

**Prerequisites**
Python 3.8 or higher
Telegram Bot Token (obtained via BotFather)
Firebase project with Firestore enabled and a service account key
Dependencies: python-telegram-bot, firebase-admin
