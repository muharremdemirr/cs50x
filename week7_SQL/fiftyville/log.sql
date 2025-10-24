-- Keep a log of any SQL queries you execute as you solve the mystery.

-- To know about the crime itself
SELECT description FROM crime_scene_reports WHERE
   year = 2024 AND month = 7 AND day = 28
    AND street = 'Humphrey Street';

-- According to interviews crime took place at bakery.
-- I wanted to see the license plates of cars at that time.
SELECT license_plate, minute from bakery_security_logs WHERE
    year = 2024 AND month = 7 AND day = 28 AND
    hour = 10 AND minute >= 15 AND  minute <= 26;

-- I analyzed the interviews I was right about the licanse plates
-- findings: thief escaped 10 min after the theft from the parking lot
--   thief withdrawn some money from ATM that Leggett Street at the morning
--   also, called somebody to know about the plane ticket tomorrow as soon as possible
SELECT name, transcript FROM interviews WHERE
     year = 2024 AND month = 7 AND day = 28;

-- To people's info who are related to bakery cc tv logs at crime day
SELECT bakery_security_logs.minute, people.license_plate, people.name, people.phone_number, people.passport_number
   FROM people
    JOIN bakery_security_logs
    ON people.license_plate = bakery_security_logs.license_plate
    WHERE year = 2024 AND month = 7 AND day = 28 AND
    hour = 10 AND minute >= 15 AND  minute <= 26;

-- To see which people withdrew money from their bank accounts at the crime day at Leggett Street at the morning
SELECT DISTINCT(people.name), bank_accounts.account_number, atm.amount FROM people
    JOIN bank_accounts ON people.id = bank_accounts.person_id
    JOIN atm_transactions AS atm ON bank_accounts.account_number = atm.account_number
    WHERE year = 2024 AND month = 7 AND day = 28 AND
    atm_location = 'Leggett Street' AND transaction_type = 'withdraw'
    ORDER BY atm.amount DESC;

--    (SELECT account_number FROM atm_transactions WHERE
--    year = 2024 AND month = 7 AND day = 28 AND
--    atm_location = 'Leggett Street' AND transaction_type = 'withdraw')

-- To analyze phone calls and see callers and receivers together
SELECT caller_person.name AS caller_name, caller, receiver_person.name AS receiver_name, receiver, duration FROM phone_calls
    JOIN people AS caller_person  ON phone_calls.caller = caller_person.phone_number
    JOIN people AS receiver_person ON phone_calls.receiver = receiver_person.phone_number
    WHERE year = 2024 AND month = 7 AND day = 28 AND duration < 60
    ORDER BY duration;
-- Flights from Fiftyville

 SELECT dest.city, hour, minute  FROM flights
   JOIN airports AS dest ON destination_airport_id = dest.id
   WHERE origin_airport_id =
   (SELECT id FROM airports WHERE city = 'Fiftyville')
   AND year = 2024 AND month = 7 AND day = 29
   ORDER BY hour, minute;

-- To see every data we agot from the database
-- we got 3 columns of data here
SELECT people.name, dest.city, hour, minute FROM flights
    JOIN passengers ON flights.id = passengers.flight_id
    JOIN people ON passengers.passport_number = people.passport_number
    JOIN airports AS dest ON dest.id = destination_airport_id
    WHERE destination_airport_id IN
            (SELECT destination_airport_id FROM flights
                JOIN airports ON destination_airport_id = airports.id
                    WHERE origin_airport_id =
                        (SELECT id FROM airports WHERE city = 'Fiftyville'))
        AND
            people.phone_number IN
                 (SELECT caller FROM phone_calls
                      WHERE year = 2024 AND month = 7 AND day = 28 AND duration < 60)
        AND
            people.passport_number IN
            (SELECT passport_number FROM people
                 JOIN bank_accounts ON people.id = bank_accounts.person_id
                WHERE bank_accounts.account_number IN
                 (SELECT account_number FROM atm_transactions
                     WHERE year = 2024 AND month = 7 AND day = 28 AND
                     atm_location = 'Leggett Street' AND transaction_type = 'withdraw'))
        AND
            people.passport_number IN
            (SELECT passport_number FROM people
                JOIN bakery_security_logs ON people.license_plate = bakery_security_logs.license_plate
                WHERE year = 2024 AND month = 7 AND day = 28
                AND hour = 10 AND minute >= 15 AND minute <= 26)
    ORDER BY hour, minute;
