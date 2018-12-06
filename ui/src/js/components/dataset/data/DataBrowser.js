// vendor
import React, { Component } from 'react';
import { createPaginationContainer, graphql } from 'react-relay';
// mutations
import FileBrowserWrapper from 'Components/labbook/fileBrowser/FileBrowserWrapper';
// store
import store from 'JS/redux/store';

class DataBrowser extends Component {
  constructor(props) {
  	super(props);

    this.state = {
      rootFolder: '',
      moreLoading: false,
    };

    this.setRootFolder = this.setRootFolder.bind(this);
    this._loadMore = this._loadMore.bind(this);
  }

  /*
    loads more if branches are switched
  */
  componentDidUpdate() {
    this.props.loadStatus(this.state.moreLoading);
    if (!this.state.moreLoading && this.props.data.allFiles && this.props.data.allFiles.edges.length < 3 && this.props.data.allFiles.pageInfo.hasNextPage) {
      this._loadMore();
    }
  }

  /*
    handle state and addd listeners when component mounts
  */
  componentDidMount() {
    this.props.loadStatus(this.state.moreLoading);
    if (this.props.data.allFiles &&
      this.props.data.allFiles.pageInfo.hasNextPage) {
      this._loadMore(); // routes query only loads 2, call loadMore
    } else {
      this.setState({ moreLoading: false });
    }
  }
  /*
    @param
    triggers relay pagination function loadMore
    increments by 100
    logs callback
  */
  _loadMore() {
    this.setState({ moreLoading: true });
    const self = this;
    this.props.relay.loadMore(
      100, // Fetch the next 100 feed items
      (response, error) => {
        if (error) {
          console.error(error);
        }

        if (self.props.data.allFiles &&
         self.props.data.allFiles.pageInfo.hasNextPage) {
          self._loadMore();
        } else {
          this.setState({ moreLoading: false });
        }
      },
    );
  }
  /*
    @param
    sets root folder by key
    loads more files
  */
  setRootFolder(key) {
    this.setState({ rootFolder: key });
  }

  render() {
    if (this.props.data && this.props.data.allFiles) {
      let dataFiles = this.props.data.allFiles;
      if (this.props.data.allFiles.edges.length === 0) {
        dataFiles = {
          edges: [],
          pageInfo: this.props.data.allFiles.pageInfo,
        };
      }

      return (
        <FileBrowserWrapper
          ref="dataBrowser"
          section="data"
          selectedFiles={this.props.selectedFiles}
          clearSelectedFiles={this.props.clearSelectedFiles}
          setRootFolder={this.setRootFolder}
          files={dataFiles}
          parentId={this.props.dataId}
          connection="DataBrowser_allFiles"
          favoriteConnection="DataFavorites_favorites"
          favorites={this.props.favorites}
          isLocked={{ locked: false }}
          {...this.props}
        />
      );
    }
    return (<div>No Files Found</div>);
  }
}

export default createPaginationContainer(
  DataBrowser,
  {

    data: graphql`
      fragment DataBrowser_data on Dataset{
        allFiles(after: $cursor, first: $first)@connection(key: "DataBrowser_allFiles", filters: []){
          edges{
            node{
              id
              isDir
              isFavorite
              modifiedAt
              key
              size
            }
            cursor
          }
          pageInfo{
            hasNextPage
            hasPreviousPage
            startCursor
            endCursor
          }
        }
      }`,
  },
  {
    direction: 'forward',
    getConnectionFromProps(props) {
      return props.data && props.data.allFiles;
    },
    getFragmentVariables(prevVars, totalCount) {
      return {
        ...prevVars,
        first: totalCount,
      };
    },
    getVariables(props, { count, cursor }, fragmentVariables) {
      const { owner, labbookName } = store.getState().routes;

      return {
        first: count,
        cursor,
        owner,
        name: labbookName,
      };
    },
    query: graphql`
      query DataBrowserPaginationQuery(
        $first: Int
        $cursor: String
        $owner: String!
        $name: String!
      ) {
        dataset(name: $name, owner: $owner){
           id
           description
           ...DataBrowser_data
        }
      }
    `,
  },

);
