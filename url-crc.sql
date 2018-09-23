BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "url_crc" (
        `url`   TEXT NOT NULL UNIQUE,
        `crc32` INTEGER NOT NULL UNIQUE,
        `from_addon`    TEXT
);

CREATE TABLE IF NOT EXISTS "addons" (
        `url`   TEXT NOT NULL,
        `checked`       INTEGER NOT NULL DEFAULT 0
);
COMMIT;