// vendor
import React, { Component } from 'react';
import { Route, Switch } from 'react-router-dom';
import { createFragmentContainer, graphql } from 'react-relay';
import { DragDropContext } from 'react-dnd';
import HTML5Backend from 'react-dnd-html5-backend';
import classNames from 'classnames';
import { connect } from 'react-redux';
import Loadable from 'react-loadable';
// store
import store from 'JS/redux/store';
import { setStickyState } from 'JS/redux/reducers/dataset/dataset';
import { setCallbackRoute } from 'JS/redux/reducers/routes';
// config
import Config from 'JS/config';
// utils
import { getFilesFromDragEvent } from 'JS/utils/html-dir-content';
// components
import Login from 'Components/login/Login';
import Loader from 'Components/common/Loader';
import ErrorBoundary from 'Components/common/ErrorBoundary';
import DatasetHeader from '../shared/header/Header';
// assets
import './Dataset.scss';

const Loading = () => <Loader />;

const Overview = Loadable({
  loader: () => import('./overview/DatasetOverviewContainer'),
  loading: Loading,
  delay: 500,
});

const Activity = Loadable({
  loader: () => import('./activity/DatasetActivityContainer'),
  loading: Loading,
  delay: 500,
});

const Data = Loadable({
  loader: () => import('./data/Data'),
  loading: Loading,
  delay: 500,
});

class Dataset extends Component {
  constructor(props) {
  	super(props);

    localStorage.setItem('owner', store.getState().routes.owner);
    this.state = {};
    // bind functions here
    this._setBuildingState = this._setBuildingState.bind(this);
    setCallbackRoute(props.location.pathname);
    const { labbookName, owner } = store.getState().routes;
    document.title = `${owner}/${labbookName}`;
  }
  /**
    @param {object} nextProps
    @param {object} state
    calls setCallbackRoute on prop change
  */
  static getDerivedStateFromProps(nextProps, state) {
    setCallbackRoute(nextProps.location.pathname);
    return state;
  }
  /**
    @param {}
    subscribe to store to update state
    set unsubcribe for store
  */
  componentDidMount() {
    this.props.auth.isAuthenticated().then((response) => {
      let isAuthenticated = response;
      if (isAuthenticated === null) {
        isAuthenticated = false;
      }
      if (isAuthenticated !== this.state.authenticated) {
        this.setState({ authenticated: isAuthenticated });
      }
    });
    this._setStickHeader();

    window.addEventListener('scroll', this._setStickHeader);
  }

  /**
    @param {}
    removes event listeners
  */
  componentWillUnmount() {
    window.removeEventListener('scroll', this._setStickHeader);
  }

  /**
    @param {}
    dispatches sticky state to redux to update state
  */
  _setStickHeader() {
    const isExpanded = (window.pageYOffset < this.offsetDistance) && (window.pageYOffset > 120);
    this.offsetDistance = window.pageYOffset;
    const sticky = 50;
    const isSticky = window.pageYOffset >= sticky;
    if ((store.getState().dataset.isSticky !== isSticky) || (store.getState().dataset.isExpanded !== isExpanded)) {
      setStickyState(isSticky, isExpanded);
    }
  }

  /**
    @param {boolean} isBuilding
    updates container status state
    updates dataset state
  */
  _setBuildingState = (isBuilding) => {
    this.refs.ContainerStatus && this.refs.ContainerStatus.setState({ isBuilding });

    if (this.props.isBuilding !== isBuilding) {
      setBuildingState(isBuilding);
    }
  }

  /**
    scrolls to top of window
  */
  _scrollToTop() {
    window.scrollTo(0, 0);
  }

  render() {
    if (this.props.dataset) {
      const { dataset } = this.props;
      const datasetCSS = classNames({
        Dataset: true,
        'Dataset--detail-mode': this.props.detailMode,
        'Dataset--demo-mode': window.location.hostname === Config.demoHostName,
      });

      return (
        <div className={datasetCSS}>

          <div className="Dataset__spacer flex flex--column">

            <DatasetHeader
              description={dataset.description}
              toggleBranchesView={() => {}}
              branchName={''}
              dataset={dataset}
              sectionType={'dataset'}
              {...this.props}
            />

            <div className="Dataset__routes flex flex-1-0-auto">

              <Switch>
                <Route
                  exact
                  path={`${this.props.match.path}`}
                  render={() => (
                    <ErrorBoundary type="datasetSectionError" key="overview">
                      <Overview
                        key={`${this.props.datasetName}_overview`}
                        dataset={dataset}
                        isManaged={dataset.datasetType.isManaged}
                        datasetId={dataset.id}
                        scrollToTop={this._scrollToTop}
                        sectionType="dataset"
                        datasetType={dataset.datasetType}
                        />
                    </ErrorBoundary>
                  )}
                />

                <Route path={`${this.props.match.path}/:datasetMenu`}>

                  <Switch>

                    <Route
                      path={`${this.props.match.path}/overview`}
                      render={() => (
                        <ErrorBoundary
                          type="datasetSectionError"
                          key="activity"
                        >

                          <Overview
                            key={`${this.props.datasetName}_overview`}
                            dataset={dataset}
                            isManaged={dataset.datasetType.isManaged}
                            datasetId={dataset.id}
                            scrollToTop={this._scrollToTop}
                            sectionType="dataset"
                            datasetType={dataset.datasetType}
                             />

                        </ErrorBoundary>
                          )}
                    />
                    <Route
                      path={`${this.props.match.path}/activity`}
                      render={() => (
                        <ErrorBoundary
                          type="datasetSectionError"
                          key="activity"
                        >

                          <Activity
                               key={`${this.props.datasetName}_activity`}
                               dataset={dataset}
                               activityRecords={this.props.activityRecords}
                               datasetId={dataset.id}
                               activeBranch={dataset.activeBranch}
                               sectionType={'dataset'}
                               {...this.props}
                             />

                        </ErrorBoundary>
                          )}
                    />
                    <Route
                      path={`${this.props.match.url}/data`}
                      render={() => (
                        <ErrorBoundary
                          type="datasetSectionError"
                          key="code"
                        >

                          <Data
                               dataset={dataset}
                               datasetId={dataset.id}
                               type="dataset"
                               section="data"
                             />

                        </ErrorBoundary>)}
                    />

                  </Switch>

                </Route>

              </Switch>

            </div>

          </div>

          <div className="Dataset__veil" />

        </div>);
    }

    if (this.state.authenticated) {
      return (<Loader />);
    }

    return (<Login auth={this.props.auth} />);
  }
}

const mapStateToProps = (state, ownProps) => state.dataset;

const mapDispatchToProps = dispatch => ({
});

const DatasetContainer = connect(mapStateToProps, mapDispatchToProps)(Dataset);


const DatasetFragmentContainer = createFragmentContainer(
  DatasetContainer,
  {
    dataset: graphql`
      fragment Dataset_dataset on Dataset{
          id
          description
          owner
          name
          #createdOnUtc
          modifiedOnUtc
          defaultRemote
          visibility
          datasetType {
              name
              storageType
              description
              readme
              tags
              icon
              url
              isManaged
          }
          ...Data_dataset
          ...DatasetActivityContainer_dataset
          ...DatasetOverviewContainer_dataset
      }`,
  },

);

const backend = (manager: Object) => {
  const backend = HTML5Backend(manager),
    orgTopDropCapture = backend.handleTopDropCapture;

  backend.handleTopDropCapture = (e) => {
    e.preventDefault();
    if (backend.currentNativeSource) {
      orgTopDropCapture.call(backend, e);

      backend.currentNativeSource.item.dirContent = getFilesFromDragEvent(e, { recursive: true }); // returns a promise
    }
  };

  return backend;
};

export default DragDropContext(backend)(DatasetFragmentContainer);
