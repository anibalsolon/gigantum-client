import sys
import pprint

from misc import (gqlquery as run_query, endpt_post)


migrate_query = '''
query BasicLabbookQuery(
    $owner: String!,
    $labbookName: String!
) {
    labbook(owner: $owner, name: $labbookName) {
        activeBranchName
        creationDateUtc
        isRepoClean
        schemaVersion
        isDeprecated
        environment {
            imageStatus
            containerStatus
        }
    }
}
'''

if __name__ == '__main__':
    owner, lbname = sys.argv[1:3]
    endpoint = endpt_post
    print(owner, lbname)

    resp = run_query(endpoint, 'Migrate Labbook', migrate_query, variables={'owner': owner, 'labbookName': lbname})
    pprint.pprint(resp)

