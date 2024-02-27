from mo_sql_parsing import parse_bigquery as parse
from databathing.py_bathing import py_bathing
import json
import copy

class Pipeline:
    def __init__(self, query):
        self.parsed_whole_query = parse(query)
        self.parsed_json_whole_query = json.loads(json.dumps(self.parsed_whole_query, indent=4))
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
        self.last_ans = "final_df = spark.read.table(\"" + tmp_query["from"]["value"] + "\")\\" + dbing.parse() + "\n\n"

    def parse(self):
        final_ans = ""
        if "with" in self.parsed_json_whole_query:
            self.gen_with_pipeline(self.parsed_json_whole_query)
            final_ans += self.with_ans
        self.gen_last_pipeline(self.parsed_json_whole_query)
        final_ans += self.last_ans
        return final_ans

# Example usage
query = "SELECT col1, col2 FROM table_name WHERE col3 = 'value' GROUP BY col1 ORDER BY col2 DESC LIMIT 10"
pipeline = Pipeline(query)
ans = pipeline.parse()
print(ans)
