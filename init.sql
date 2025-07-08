-- Create a table
CREATE TABLE core_click_1 (
                                                 click_id integer NULL,
                                                 banner_id integer NULL,
                                                 campaign_id integer NULL

);

-- Copy data from the CSV file into the table
COPY core_click_1 FROM '/cleaned_csv/1/clicks_1.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE core_click_2 (
                                                 click_id integer NULL,
                                                 banner_id integer NULL,
                                                 campaign_id integer NULL

);

-- Copy data from the CSV file into the table
COPY core_click_2 FROM '/cleaned_csv/2/clicks_2.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE core_click_3 (
                                                 click_id integer NULL,
                                                 banner_id integer NULL,
                                                 campaign_id integer NULL

);

-- Copy data from the CSV file into the table
COPY core_click_3 FROM '/cleaned_csv/3/clicks_3.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE core_click_4 (
                                                 click_id integer NULL,
                                                 banner_id integer NULL,
                                                 campaign_id integer NULL

);

-- Copy data from the CSV file into the table
COPY core_click_4 FROM '/cleaned_csv/4/clicks_4.csv' DELIMITER ',' CSV HEADER;
-- Create a table
CREATE TABLE core_conversions_1 (
                                                 conversion_id integer NULL,
                                                 click_id integer NULL,
                                                 revenue TEXT NULL

);

-- Copy data from the CSV file into the table
COPY core_conversions_1 FROM '/cleaned_csv/1/conversions_1.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE core_conversions_2 (
                                    conversion_id integer NULL,
                                    click_id integer NULL,
                                    revenue TEXT NULL
);

-- Copy data from the CSV file into the table
COPY core_conversions_2 FROM '/cleaned_csv/2/conversions_2.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE core_conversions_3 (
                                    conversion_id integer NULL,
                                    click_id integer NULL,
                                    revenue TEXT NULL

);

-- Copy data from the CSV file into the table
COPY core_conversions_3 FROM '/cleaned_csv/3/conversions_3.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE core_conversions_4 (
                                    conversion_id integer NULL,
                                    click_id integer NULL,
                                    revenue TEXT NULL

);

-- Copy data from the CSV file into the table
COPY core_conversions_4 FROM '/cleaned_csv/4/conversions_4.csv' DELIMITER ',' CSV HEADER;


-- Create a table
CREATE TABLE core_impressions_1 (
                                                 banner_id integer NULL,
                                                 campaign_id integer NULL

);

-- Copy data from the CSV file into the table
COPY core_impressions_1 FROM '/cleaned_csv/1/impressions_1.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE core_impressions_2 (
                                                 banner_id integer NULL,
                                                 campaign_id integer NULL

);

-- Copy data from the CSV file into the table
COPY core_impressions_2 FROM '/cleaned_csv/2/impressions_2.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE core_impressions_3 (
                                                 banner_id integer NULL,
                                                 campaign_id integer NULL

);

-- Copy data from the CSV file into the table
COPY core_impressions_3 FROM '/cleaned_csv/3/impressions_3.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE core_impressions_4 (
                                                 banner_id integer NULL,
                                                 campaign_id integer NULL

);

-- Copy data from the CSV file into the table
COPY core_impressions_4 FROM '/cleaned_csv/4/impressions_4.csv' DELIMITER ',' CSV HEADER;
