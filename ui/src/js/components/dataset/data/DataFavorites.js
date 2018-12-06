// // vendor
// import React, { Component } from 'react';
// import { createPaginationContainer, graphql } from 'react-relay';
// // componenets
// import DataFavoriteList from './DataFavoriteList';
// import FileEmpty from 'Components/dataset/overview/FileEmpty';
// // store
// import store from 'JS/redux/store';

// class DataFavorites extends Component {
//   constructor(props) {
//   	super(props);
//     this.state = {
//       loading: false,
//     };
//   }
//   /*
//     update component when props are reloaded
//   */
//   UNSAFE_componentWillReceiveProps(nextProps) {
//     // this._loadMore() //routes query only loads 2, call loadMore
//     if (nextProps.data && nextProps.data.favorites && nextProps.data.favorites.pageInfo.hasNextPage && nextProps.data.favorites.edges.length < 3) {
//       this.props.relay.loadMore(
//         1, // Fetch the next 10 feed items
//         (response, error) => {
//           if (error) {
//             console.error(error);
//           }
//         },
//       );
//     }
//   }

//   /**
//     handle state and addd listeners when component mounts
//   */
//   componentDidMount() {
//     // this._loadMore() //routes query only loads 2, call loadMore
//     if (this.props.data && this.props.data.favorites && this.props.data.favorites.pageInfo.hasNextPage && this.props.data.favorites.edges.length < 3) {
//       this.props.relay.loadMore(
//         1, // Fetch the next 10 feed items
//         (response, error) => {
//           if (error) {
//             console.error(error);
//           }
//         },
//       );
//     }
//   }

//   /**
//     @param
//     triggers relay pagination function loadMore
//     increments by 10
//     logs callback
//   */
//   _loadMore() {
//     const self = this;

//     this.setState({ loading: true });

//     this.props.relay.loadMore(
//       3, // Fetch the next 10 feed items
//       (response, error) => {
//         self.setState({ loading: false });

//         if (error) {
//           console.error(error);
//         }
//       },
//     );
//   }


//   render() {
//     if (this.props.data && this.props.data.favorites) {
//       let loadingClass = (this.props.data.favorites.pageInfo.hasNextPage) ? 'Favorite__action-bar' : 'hidden';
//       loadingClass = (this.state.loading) ? 'Favorite__action-bar--loading' : loadingClass;

//       if (this.props.data.favorites.edges.length > 0) {
//         const favorites = this.props.data.favorites.edges.filter(edge => edge && (edge.node !== undefined));

//         return (

//           <div className="Favorite">
//             <DataFavoriteList
//               datasetName={this.props.datasetName}
//               dataId={this.props.dataId}
//               section="data"
//               favorites={favorites}
//               owner={this.props.owner}
//             />


//             <div className={loadingClass}>
//               <button
//                 className="Favorite__load-more"
//                 onClick={() => { this._loadMore(); }}
//               >
//                 Load More
//               </button>
//             </div>
//           </div>

//         );
//       }
//       return (
//         <FileEmpty
//           section="data"
//           mainText="This Project has No Data Favorites"
//         />
//       );
//     }
//     return (<div>No Files Found</div>);
//   }
// }

// export default createPaginationContainer(
//   DataFavorites,
//   {

//     data: graphql`
//       fragment DataFavorites_data on DatasetFileConnection{
//         favorites(after: $cursor, first: $first)@connection(key: "DataFavorites_favorites"){
//           edges{
//             node{
//               id
//               owner
//               name
//               index
//               key
//               description
//               isDir
//               associatedDatasetFileId
//               section
//             }
//             cursor
//           }
//           pageInfo{
//             hasNextPage
//             hasPreviousPage
//             startCursor
//             endCursor
//           }
//         }
//       }`,
//   },
//   {
//     direction: 'forward',
//     getConnectionFromProps(props) {
//       return props.data && props.data.favorites;
//     },
//     getFragmentVariables(prevVars, totalCount) {
//       return {
//         ...prevVars,
//         first: totalCount,
//       };
//     },
//     getVariables(props, { count, cursor }, fragmentVariables) {
//       const { owner, datasetName } = store.getState().routes;
//       return {
//         first: count,
//         cursor,
//         owner,
//         name: datasetName,
//       };
//     },
//     query: graphql`
//       query DataFavoritesPaginationQuery(
//         $first: Int
//         $cursor: String
//         $owner: String!
//         $name: String!
//       ) {
//         dataset(name: $name, owner: $owner){
//            id
//            description
//            # You could reference the fragment defined previously.
//            ...DataFavorites_data
//         }
//       }
//     `,
//   },

// );
