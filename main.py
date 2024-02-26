import sqlparse

def sql_to_pyspark(sql_query):
    # Parse the SQL query
    parsed = sqlparse.parse(sql_query)
    statement = parsed[0]

    # Extract the main components of the SQL query
    tokens = statement.tokens
    command = tokens[0].value.lower()

    if command == 'select':
        # Extract the columns, tables, and optional conditions
        columns = []
        tables = []
        for token in tokens[2:]:
            if token.value.lower() == 'from':
                break
            if isinstance(token, sqlparse.sql.IdentifierList):
                for iden in token.get_identifiers():
                    columns.append(iden.get_real_name())
            elif isinstance(token, sqlparse.sql.Identifier):
                columns.append(token.get_real_name())
        for token in tokens:
            if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'FROM':
                from_index = tokens.index(token)
                break
        for token in tokens[from_index:]:
            if isinstance(token, sqlparse.sql.IdentifierList):
                for iden in token.get_identifiers():
                    tables.append(iden.get_real_name())
            elif isinstance(token, sqlparse.sql.Identifier):
                tables.append(token.get_real_name())

        # Construct the PySpark code
        pyspark_code = f"df = spark.read.table('{tables[0]}').select('{', '.join(columns)}')\n"
        pyspark_code += "df.show()"

        return pyspark_code

    else:
        return "Unsupported SQL command"

# Example SQL query with column name only
sql_query = "SELECT t FROM t1"
pyspark_code = sql_to_pyspark(sql_query)
print(pyspark_code)
