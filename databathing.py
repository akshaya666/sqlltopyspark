from mo_sql_parsing import parse_bigquery as parse
from mo_sql_parsing import format
import json
import copy

class py_bathing:
    def __init__(self, parsed_json_whole_query):
        self.parsed_json_whole_query = parsed_json_whole_query
        self.distinct_flag = False
        self.from_ans = ""
        self.select_ans = ""
        self.level_select = 0
        self.where_ans = ""
        self.groupby_ans = ""
        self.limit_ans = ""
        self.agg_ans = ""
        self.having_ans = ""
        self.orderby_ans = ""
        self.agg_list = ["sum", "avg", "max", "min", "mean", "count", "collect_list", "collect_set"]

    def _from_analyze(self, from_stmt):
        if not from_stmt:
            return
        if type(from_stmt) is str:
            self.from_ans += format({"from": from_stmt})[5:]
        elif type(from_stmt) is dict:
            if "name" in from_stmt.keys():
                self.from_ans += from_stmt['value'] + ".alias(\"" + from_stmt['name'] + "\")."
            elif "left join" in from_stmt.keys():
                self.from_ans += "join({}, {}, \"{}\").".format(
                    from_stmt['left join']['value'] + ".alias(\"" + from_stmt['left join']['name'] + "\")",
                    "col(\"" + str(from_stmt['on']['eq'][0]) + "\")" + "==" + "col(\"" + str(
                        from_stmt['on']['eq'][1]) + "\")",
                    'left')
            elif "inner join" in from_stmt.keys():
                self.from_ans += "join({}, {}, \"{}\").".format(
                    from_stmt['inner join']['value'] + ".alias(\"" + from_stmt['inner join']['name'] + "\")",
                    "col(\"" + str(from_stmt['on']['eq'][0]) + "\")" + "==" + "col(\"" + str(
                        from_stmt['on']['eq'][1]) + "\")",
                    'inner')
            elif "right join" in from_stmt.keys():
                self.from_ans += "join({}, {}, \"{}\").".format(
                    from_stmt['right join']['value'] + ".alias(\"" + from_stmt['right join']['name'] + "\")",
                    "col(\"" + str(from_stmt['on']['eq'][0]) + "\")" + "==" + "col(\"" + str(
                        from_stmt['on']['eq'][1]) + "\")",
                    'right')

        elif type(from_stmt) is list:
            for item_from in from_stmt:
                self._from_analyze(item_from)

    def _select_analyze(self, select_stmt):
        if not select_stmt:
            return

        if type(select_stmt) is str:
            self.select_ans += "\"" + format({"select": select_stmt})[7:] + "\","
            return
        if type(select_stmt) is dict and type(select_stmt['value']) is str:
            self.select_ans += "\"" + format({"select": select_stmt})[7:] + "\","
            return
        if type(select_stmt) is dict:
            if list(select_stmt["value"].keys())[0].lower() in self.agg_list:
                self.select_ans += "\"" + select_stmt['name'] + "\","
            elif list(select_stmt["value"].keys())[0].lower() == "create_struct":
                self.select_ans += "\"" + format({"select": select_stmt})[14:] + "\","
            else:
                self.select_ans += "\"" + format({"select": select_stmt})[7:] + "\","
        elif type(select_stmt) is list and (self.level_select == 0):
            self.level_select += 1
            for inner_item in select_stmt:
                self._select_analyze(inner_item)

    def _where_analyze(self, where_stmt):
        if not where_stmt:
            return

        if type(where_stmt) is str:
            self.where_ans = format({"where": where_stmt})[6:]
        elif type(where_stmt) is dict:
            if "and" in where_stmt:
                and_conditions = where_stmt["and"]
                self.where_ans = " and ".join([format({"where": cond})[6:] for cond in and_conditions])
            elif "or" in where_stmt:
                or_conditions = where_stmt["or"]
                self.where_ans = " or ".join([format({"where": cond})[6:] for cond in or_conditions])
            else:
                self.where_ans = format({"where": where_stmt})[6:]

    def _groupby_analyze(self, groupby_stmt):
        self.groupby_ans = format({"groupby": groupby_stmt})[9:]

    def _agg_analyze(self, agg_stmt):
        if type(agg_stmt) is dict:
            if type(agg_stmt["value"]) is dict and list(agg_stmt["value"].keys())[0].lower() in self.agg_list:
                for funct, alias in agg_stmt["value"].items():
                    self.agg_ans += "{}(col(\"{}\")).alias(\"{}\"),".format(funct, alias, agg_stmt["name"])

        elif type(agg_stmt) is list:
            for item in agg_stmt:
                self._agg_analyze(item)

        self.agg_ans = self.agg_ans.replace("\n", "")

    def _having_analyze(self, having_stmt):
        self.having_ans = format({"having": having_stmt})[7:]

    def _orderby_analyze(self, order_stmt):
        if type(order_stmt) is dict:
            odr = "desc()" if order_stmt.get("sort", "asc") == "desc" else "asc()"
            self.orderby_ans += "col(\"{}\").{},".format(str(order_stmt["value"]), odr)
        else:
            for item in order_stmt:
                self._orderby_analyze(item)

    def _limit_analyze(self, limit_stmt):
        self.limit_ans = limit_stmt

    def parse(self):
        from_final_ans = where_final_ans = groupby_final_ans = agg_final_ans = select_final_ans = orderby_final_ans = limit_final_ans = having_final_ans = ""

        for method, stmt in self.parsed_json_whole_query.items():
            if str(method).lower() == "from":
                self._from_analyze(stmt)
                from_final_ans = self.from_ans[:-1] if self.from_ans[-1] == '.' else self.from_ans

            elif str(method).lower() == "where":
                self._where_analyze(stmt)
                where_final_ans = self.where_ans

            elif str(method).lower() == "groupby":
                self._groupby_analyze(stmt)
                groupby_final_ans = self.groupby_ans
                agg_stmt = self.parsed_json_whole_query["select"] \
                    if "select" in self.parsed_json_whole_query.keys() \
                    else self.parsed_json_whole_query["select_distinct"]
                self._agg_analyze(agg_stmt)
                agg_final_ans = self.agg_ans[:-1]

            elif str(method).lower() in ["select", "select_distinct"]:
                self._select_analyze(stmt)
                select_final_ans = self.select_ans[:-1]
                self.distinct_flag = True if str(method) == "select_distinct" else False

            elif str(method) == "having":
                self._having_analyze(stmt)
                having_final_ans = self.having_ans

            elif str(method) == "orderby":
                self._orderby_analyze(stmt)
                orderby_final_ans = self.orderby_ans[:-1]

            elif str(method).lower() == "limit":
                self._limit_analyze(stmt)
                limit_final_ans = self.limit_ans

        final_ans = ""
        if from_final_ans:
            final_ans += from_final_ans + "\\"
        if where_final_ans:
            final_ans += "\n.filter(\"{}\")\\".format(where_final_ans)
        if groupby_final_ans:
            final_ans += "\n.groupBy(\"{}\")\\".format(groupby_final_ans)
        if agg_final_ans:
            final_ans += "\n.agg({})\\".format(agg_final_ans)
        if having_final_ans:
            final_ans += "\n.filter(\"{}\")\\".format(having_final_ans)
        if select_final_ans:
            final_ans += "\n.selectExpr({})\\".format(select_final_ans)
        if self.distinct_flag:
            final_ans += "\n.distinct()\\"
        if orderby_final_ans:
            final_ans += "\n.orderBy(" + orderby_final_ans + ")\\"
        if limit_final_ans:
            final_ans += "\n.limit(" + str(limit_final_ans) + ")\\"

        return final_ans[:-1]

class Pipeline:
    def __init__(self, query):
        self.parsed_whole_query = parse(query)
        self.parsed_json_whole_query = json.loads(json.dumps(self.parsed_whole_query, indent=4))
        self.parsed_json_whole_query = self.parsed_json_whole_query
        self.with_ans = ""
        self.last_ans = ""

    def gen_with_pipeline(self, query):
        if "with" in query:
            with_stmts = query["with"]
            if type(with_stmts) is dict:
                self.gen_with_pipeline(with_stmts)
            else:
                for with_stmt in with_stmts:
                    self.gen_with_pipeline(with_stmt)
        else:
            dbing = py_bathing(query["value"])
            self.with_ans += query["name"] + " = " + dbing.parse() + "\n\n"

    def gen_last_pipeline(self, query):
        tmp_query = copy.deepcopy(query)

        if "with" in query:
            del tmp_query["with"]

        dbing = py_bathing(tmp_query)
        self.last_ans = "final_df = " + dbing.parse() + "\n\n"

    def parse(self):
        final_ans = ""
        if "with" in self.parsed_json_whole_query:
            self.gen_with_pipeline(self.parsed_json_whole_query)
            final_ans += self.with_ans
        self.gen_last_pipeline(self.parsed_json_whole_query)
        final_ans += self.last_ans
        return final_ans

# Example usage
query = """
    SELECT 
        col1, col2 
    FROM 
        table_name 
    WHERE 
        col3 = 'value1' 
        AND col4 = 'value2' 
        OR (col5 = 'value3' AND col6 = 'value4') 
    GROUP BY 
        col1 
    ORDER BY 
        col2 DESC 
    LIMIT 
        10
"""

pipeline = Pipeline(query)
ans = pipeline.parse()
print(ans)
