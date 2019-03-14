const labbookUpdatesQuery = graphql`
  query fetchLabbookUpdateQuery($name: String!, $owner: String!){
  labbook(name: $name, owner: $owner){
    environment{
      containerStatus
      imageStatus
    }
    collaborators{
      id
      owner
      name
      collaboratorUsername
      permission
    }
    canManageCollaborators
    visibility
    defaultRemote
    branches {
      id
      owner
      name
      branchName
      isActive
      isLocal
      isRemote
      isMergeable
      commitsBehind
      commitsAhead
    }
  }
}`;

export default labbookUpdatesQuery;
