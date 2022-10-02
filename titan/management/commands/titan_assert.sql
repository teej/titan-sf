CREATE FUNCTION titan_assert(assertion BOOLEAN)
    RETURNS BOOLEAN
    LANGUAGE JAVASCRIPT
AS
$$
    if(ASSERTION) {
        return true;
    } else {
        throw 'Assertion Error';
    }
$$
;

CREATE FUNCTION titan_assert(assertion BOOLEAN, message VARCHAR)
    RETURNS BOOLEAN
    LANGUAGE JAVASCRIPT
AS
$$
    if(ASSERTION) {
        return true;
    } else {
        throw 'Assertion Error: ' + MESSAGE;
    }
$$
;