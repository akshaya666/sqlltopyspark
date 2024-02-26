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
        aliases = {}
        tables = []
        join_conditions = {}
        conditions = []
        group_by = []
        order_by = []
        table_flag = False
        join_flag = False
        group_by_flag = False
        order_by_flag = False
        on_flag = False
        having_flag = False
        for token in tokens[2:]:
            if token.value.lower() == 'from':
                table_flag = True
                continue
            if token.value.lower() in ('join', 'inner', 'outer', 'left', 'right'):
                join_flag = True
                join_type = token.value.lower()
                join_conditions[join_type] = []
                continue
            if token.value.lower() == 'group by':
                group_by_flag = True
                continue
            if token.value.lower() == 'order by':
                order_by_flag = True
                continue
            if token.value.lower() == 'on':
                on_flag = True
                continue
            if token.value.lower() == 'having':
                having_flag = True
                continue
            if table_flag and not join_flag and not group_by_flag and not order_by_flag and not having_flag:
                if isinstance(token, sqlparse.sql.IdentifierList):
                    for iden in token.get_identifiers():
                        if iden.get_real_name() != '*':
                            columns.append(iden.get_real_name())
                            if iden.has_alias():
                                aliases[iden.get_real_name()] = iden.get_alias()
                elif isinstance(token, sqlparse.sql.Identifier):
                    if token.get_real_name() != '*':
                        columns.append(token.get_real_name())
                        if token.has_alias():
                            aliases[token.get_real_name()] = token.get_alias()
                elif token.value.lower() != 'on':
                    tables.append(token)
            elif join_flag and not on_flag:
                if token.value.lower() == 'on':
                    on_flag = True
                    continue
            elif join_flag and on_flag:
                if token.value.lower() == 'and':
                    join_conditions[join_type].append([])
                    continue
                if isinstance(token, sqlparse.sql.Comparison):
                    join_conditions[join_type][-1].append(token)
            elif group_by_flag:
                if token.value.lower() != ',':
                    group_by.append(token)
            elif order_by_flag:
                if token.value.lower() != ',':
                    order_by.append(token)
            elif having_flag:
                conditions.append(token)

        # Construct the PySpark code
        pyspark_code = f"df = spark.read.table('{tables[0]}')\n"
        for join_type, condition_lists in join_conditions.items():
            for i, condition_list in enumerate(condition_lists):
                condition_str = ' and '.join(str(condition) for condition in condition_list)
                pyspark_code += f"df = df.join(spark.read.table('{tables[i+1]}'), {condition_str}, '{join_type.upper()}')\n"
        if conditions:
            filter_condition = ' and '.join(str(condition) for condition in conditions)
            pyspark_code += f"df = df.filter('{filter_condition}')\n"
        if group_by:
            group_by_cols = ', '.join(str(group) for group in group_by)
            pyspark_code += f"df = df.groupBy({group_by_cols})\n"
        if order_by:
            order_by_cols = ', '.join(str(order) for order in order_by)
            pyspark_code += f"df = df.orderBy('{order_by_cols}')\n"
        pyspark_code += "df.show()"

        return pyspark_code

    else:
        return "Unsupported SQL command"

# Example SQL query without window functions
sql_query = "SELECT column1, SUM(column2) FROM table1 GROUP BY column1 HAVING SUM(column2) > 100"
pyspark_code = sql_to_pyspark(sql_query)
print(pyspark_code)
