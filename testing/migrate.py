import sys
import pprint

from misc import (gqlquery as run_query, endpt_post)


migrate_query = '''
mutation m {{
    migrateLabbookSchema(input: {{
        owner: "{}",
        labbookName: "{}"
    }}) {{
        labbook {{
            activeBranchName
            isRepoClean
            schemaVersion
        }}
    }}
}}
'''

if __name__ == '__main__':
    owner, lbname = sys.argv[1:3]
    endpoint = endpt_post
    print(owner, lbname)
    fq = migrate_query.format(owner, lbname)
    print(fq)

    resp = run_query(endpoint, 'Migrate Labbook', fq, variables=None)
    pprint.pprint(resp)
