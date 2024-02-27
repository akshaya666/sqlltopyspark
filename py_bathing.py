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
            self.from_ans += "spark.read.table(\"{}\")".format(from_stmt)
        elif type(from_stmt) is dict:
            if "name" in from_stmt.keys():
                self.from_ans += from_stmt['value']+".alias(\""+from_stmt['name']+"\")."
            elif "left join" in from_stmt.keys():
                self.from_ans += "join({}, {}, \"{}\").".format( 
                    from_stmt['left join']['value']+".alias(\""+from_stmt['left join']['name']+"\")", 
                    "col(\""+str(from_stmt['on']['eq'][0])+"\")" + "==" + "col(\""+str(from_stmt['on']['eq'][1])+"\")" , 
                    'left')
            elif "inner join" in from_stmt.keys():
                self.from_ans += "join({}, {}, \"{}\").".format( 
                    from_stmt['inner join']['value']+".alias(\""+from_stmt['inner join']['name']+"\")", 
                    "col(\""+str(from_stmt['on']['eq'][0])+"\")" + "==" + "col(\""+str(from_stmt['on']['eq'][1])+"\")" , 
                    'inner')
            elif "right join" in from_stmt.keys():
                self.from_ans += "join({}, {}, \"{}\").".format( 
                    from_stmt['right join']['value']+".alias(\""+from_stmt['right join']['name']+"\")", 
                    "col(\""+str(from_stmt['on']['eq'][0])+"\")" + "==" + "col(\""+str(from_stmt['on']['eq'][1])+"\")" , 
                    'right')
                
        elif type(from_stmt) is list:
            for item_from in from_stmt:
                self._from_analyze(item_from)

    def _select_analyze(self, select_stmt):
        if not select_stmt:
            return

        if  type(select_stmt) is str:
            self.select_ans  += "\"" + format({ "select": select_stmt })[7:] + "\","
            return  
        if type(select_stmt) is dict and type(select_stmt['value']) is str:
            self.select_ans  += "\"" + format({ "select": select_stmt })[7:] + "\","
            return
        if type(select_stmt) is dict:
            if list(select_stmt["value"].keys())[0].lower() in self.agg_list:
                self.select_ans  += "\""+ select_stmt['name'] +"\","
            elif list(select_stmt["value"].keys())[0].lower() == "create_struct":
                self.select_ans  += "\"" + format({ "select": select_stmt })[14:] + "\","
            else:
                self.select_ans  += "\"" + format({ "select": select_stmt })[7:] + "\","
        elif type(select_stmt) is list and (self.level_select == 0):
            self.level_select += 1
            for inner_item in select_stmt:
                self._select_analyze(inner_item)

    def parse(self):
        for method, stmt in self.parsed_json_whole_query.items():
            if str(method).lower() == "from":
                self._from_analyze(stmt)
            elif str(method).lower() in ["select", "select_distinct"]:
                self._select_analyze(stmt)

        final_ans = "final_df = " + self.from_ans + "\n" + \
                    ".selectExpr([" + self.select_ans[:-1] + "])"

        return final_ans

query = "SELECT col1, col2 FROM table_name WHERE col3 = 'value' GROUP BY col1 ORDER BY col2 DESC LIMIT 10"
parsed_whole_query = parse(query)
parsed_json_whole_query = json.loads(json.dumps(parsed_whole_query,indent=4))

dbing = py_bathing(parsed_json_whole_query)
ans = dbing.parse()
print(ans)
