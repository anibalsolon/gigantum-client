// vendor
import React, { Component, Fragment } from 'react';
import { Route, Switch } from 'react-router-dom';
import shallowCompare from 'react-addons-shallow-compare';
import {
  createFragmentContainer,
  graphql,
} from 'react-relay';
import { DragDropContext } from 'react-dnd';
import HTML5Backend from 'react-dnd-html5-backend';
import classNames from 'classnames';
import { connect } from 'react-redux';
import Loadable from 'react-loadable';
import { boundMethod } from 'autobind-decorator';
// store
import store from 'JS/redux/store';
import { setContainerMenuWarningMessage } from 'JS/redux/reducers/labbook/environment/environment';
import { setMergeMode, setBuildingState, setStickyDate } from 'JS/redux/reducers/labbook/labbook';
import { setCallbackRoute } from 'JS/redux/reducers/routes';
import { setLatestPackages } from 'JS/redux/reducers/labbook/environment/packageDependencies';
import { setInfoMessage } from 'JS/redux/reducers/footer';
// utils
import { getFilesFromDragEvent } from 'JS/utils/html-dir-content';
import BranchMutations from 'Components/shared/utils/BranchMutations';
// config
import Config from 'JS/config';
// components
import Login from 'Components/login/Login';
import Loader from 'Components/common/Loader';
import ErrorBoundary from 'Components/common/ErrorBoundary';
import Header from 'Components/shared/header/Header';
import ButtonLoader from 'Components/common/ButtonLoader';
import Modal from 'Components/common/Modal';
// mutations
import LabbookContainerStatusMutation from 'Mutations/LabbookContainerStatusMutation';
import LabbookLookupMutation from 'Mutations/LabbookLookupMutation';
import MigrateProjectMutation from 'Mutations/MigrateProjectMutation';
// query
import fetchMigrationInfoQuery from './fetchMigrationInfoQuery'
// assets
import './Labbook.scss';

let count = 0;

const Loading = () => <Loader />;

/*
 * Code splitting imports intended to boost initial load speed
*/

const Overview = Loadable({
  loader: () => import('./overview/LabbookOverviewContainer'),
  loading: Loading,
});
const Activity = Loadable({
  loader: () => import('./activity/LabbookActivityContainer'),
  loading: Loading,
});
const Code = Loadable({
  loader: () => import('./code/Code'),
  loading: Loading,
});
const InputData = Loadable({
  loader: () => import('./inputData/Input'),
  loading: Loading,
});
const OutputData = Loadable({
  loader: () => import('./outputData/Output'),
  loading: Loading,
});
const Environment = Loadable({
  loader: () => import('./environment/Environment'),
  loading: Loading,
});

class Labbook extends Component {
  constructor(props) {
  	super(props);
    localStorage.setItem('owner', store.getState().routes.owner);
    // bind functions here
    this._toggleBranchesView = this._toggleBranchesView.bind(this);
    this._branchViewClickedOff = this._branchViewClickedOff.bind(this);
    setCallbackRoute(props.location.pathname);
  }

  state = {
    containerStatus: this.props.labbook.environment.containerStatus,
    imageStatus: this.props.labbook.environment.imageStatus,
    isLocked: (this.props.labbook.environment.containerStatus !== 'NOT_RUNNING') || this.props.isBuilding || this.props.isSynching || this.props.isPublishing,
    collaborators: this.props.labbook.collaborators,
    canManageCollaborators: this.props.labbook.canManageCollaborators,
    visibility: this.props.labbook.visibility,
    defaultRemote: this.props.labbook.defaultRemote,
    branches: this.props.labbook.branches,
    deletedBranches: [],
    migrationInProgress: false,
    migrateComplete: false,
    branchMutations: new BranchMutations({
      parentId: this.props.labbook.id,
      name: this.props.labbook.name,
      owner: this.props.labbook.owner,
    }),
    isDeprecated: null,
    shouldMigrate: null,
    buttonState: '',
  }

  static getDerivedStateFromProps(nextProps, state) {
    setCallbackRoute(nextProps.location.pathname);
    const propBranches = nextProps.labbook ? nextProps.labbook.branches : [];
    const stateBranches = state.branches;
    const branchMap = new Map();
    const mergedBranches = [];
    const newDeletedBranches = state.deletedBranches.slice();
    const { labbook } = nextProps;

    propBranches.forEach((branch) => {
      if (newDeletedBranches.indexOf(branch.id) === -1) {
        branchMap.set(branch.id, branch);
      }
    });
    stateBranches.forEach((branch) => {
      if (branchMap.has(branch.id)) {
        const itemReference = branchMap.get(branch.id);
        const newItem = Object.assign({}, branch, itemReference);
        branchMap.set(branch.id, newItem);
      } else {
        newDeletedBranches.push(branch.id);
      }
    });
    branchMap.forEach((branch) => {
      mergedBranches.push(branch);
    });
    const isLocked = (nextProps.labbook && nextProps.labbook.environment.containerStatus !== 'NOT_RUNNING') || nextProps.isBuilding || nextProps.isSynching || nextProps.isPublishing;

    return {
      ...state,
      deletedBranches: newDeletedBranches,
      branches: mergedBranches,
      canManageCollaborators: nextProps.labbook ? nextProps.labbook.canManageCollaborators : false,
      collaborators: nextProps.labbook ? nextProps.labbook.collaborators : [],
      isLocked,
    };
  }

  /**
    @param {}
    subscribe to store to update state
    set unsubcribe for store
  */
  componentDidMount() {
    const { props, state } = this,
          { name, owner } = props.labbook;
    this.mounted = true;
    document.title = `${owner}/${name}`;
    props.auth.isAuthenticated().then((response) => {
      let isAuthenticated = response;
      if (isAuthenticated === null) {
        isAuthenticated = false;
      }
      if ((isAuthenticated !== state.authenticated) && this.mounted) {
        this.setState({ authenticated: isAuthenticated });
      }
    });

    this._fetchMigrationInfo();

    this._setStickHeader();
    this._fetchStatus(true);

    window.addEventListener('scroll', this._setStickHeader);
    window.addEventListener('click', this._branchViewClickedOff);
  }

  /**
    @param {}
    removes event listeners
  */
  componentWillUnmount() {
    setLatestPackages({});
    this.mounted = false;
    window.removeEventListener('scroll', this._setStickHeader);

    window.removeEventListener('click', this._branchViewClickedOff);
  }

  /**
   * @param {}
   * checks if project is deprecated and should migrate and sets state
  */
  _fetchMigrationInfo() {
    const { props } = this,
          { owner, name } = props.labbook;
    let self = this;
    fetchMigrationInfoQuery.getLabook(owner, name).then((response) => {
      if (response.labbook) {
        const {
          isDeprecated,
          shouldMigrate,
        } = response.labbook;
        self.setState({
          isDeprecated,
          shouldMigrate,
        });
      }
    });
  }

  /**
  *  @param {object} - response
  *  update state from switch mutation
  *  @return {}
  */
  @boundMethod
  _updateMigationState(response) {
    if (response) {
      const { isDeprecated, shouldMigrate } = response.workonExperimentalBranch.labbook;
      this.setState({
        isDeprecated,
        shouldMigrate,
      });
    }
  }

  /**
  *  @param {}
  *  fetches status of labbook container and image
  *  sets state of labbook using redux and containerStatus using setState
  *  @return {}
  */
  _fetchStatus(isLabbookUpdate) {
    const { props, state } = this,
          { owner, name } = props.labbook,
          self = this,
          { isBuilding } = props;
    if (this.mounted) {
      if (!isLabbookUpdate) {
        LabbookContainerStatusMutation(owner, name, (error, response) => {
          if (response && response.fetchLabbookEdge && response.fetchLabbookEdge.newLabbookEdge) {
            const { environment } = response.fetchLabbookEdge.newLabbookEdge.node;
            if ((environment.imageStatus !== 'BUILD_IN_PROGRESS') && isBuilding) {
              setBuildingState(false);
            }
          }
          setTimeout(() => {
            let isLabbookUpdate = (count === 20);
            self._fetchStatus(isLabbookUpdate);
            count = isLabbookUpdate ? 0 : (count + 1);
          }, 3 * 1000);
        });
      } else {
        LabbookLookupMutation(owner, name, (error, response) => {
          if (response && response.fetchLabbookEdge && response.fetchLabbookEdge.newLabbookEdge) {
            const { branches, collaborators, canManageCollaborators } = response.fetchLabbookEdge.newLabbookEdge.node;
            self.setState({
              branches,
              collaborators,
              canManageCollaborators,
            });
          }
          setTimeout(() => {
            let isLabbookUpdate = (count === 20);
            self._fetchStatus(isLabbookUpdate);
            count = isLabbookUpdate ? 0 : (count + 1);
          }, 3 * 1000);
        });
      }
    }
  }

  /**
    @param {event}
    updates state of labbook when prompted ot by the store
    updates history prop
  */
  _branchViewClickedOff(evt) {
    if (evt.target.className.indexOf('Labbook__veil') > -1) {
      this._toggleBranchesView(false, false);
    }
  }

  /**
    sets branch uptodate in state
  */
  @boundMethod
  _setBranchUptodate() {
    const { branches } = this.state;
    const activePosition = branches.map(branch => branch.isActive).indexOf(true);
    const branchesClone = branches.slice();
    branchesClone[activePosition].commitsBehind = 0;
    branchesClone[activePosition].commitsAhead = 0;
    this.setState({ branches: branchesClone });
  }

  /**
    migrates project
  */
  @boundMethod
  _migrateProject() {
    const { owner, name } = this.props.labbook;
    this.setState({ buttonState: 'loading' });
    MigrateProjectMutation(owner, name, (response, error) => {
      if (error) {
        console.log(error);
        this.setState({ buttonState: 'error' });
        setTimeout(() => {
            this.setState({ buttonState: '' });
        }, 2000);
      } else {
        this.setState({
          isDeprecated: false,
          shouldMigrate: false,
        });
        const oldBranches = this.props.labbook.branches.filter((branch => branch.branchName.startsWith('gm.workspace')));
        oldBranches.forEach(({ branchName }, index) => {
          const data = {
            branchName,
            deleteLocal: true,
            deleteRemote: true,
          };
          this.state.branchMutations.deleteBranch(data, (response, error) => {
            if (error) {
              console.log(error);
              this.setState({ buttonState: 'error' });
              setTimeout(() => {
                  this.setState({ buttonState: '' });
              }, 2000);
            }
            if (index === oldBranches.length - 1) {
              this.setState({
                migrateComplete: true,
              });
              setInfoMessage('Project migrated successfully');
              this.setState({ buttonState: 'finished' });
              setTimeout(() => {
                this.setState({ buttonState: '' });
            }, 2000);
            }
          });
        });
      }
    });
  }

  /**
    @param {}
    dispatches sticky state to redux to update state
  */
  _setStickHeader() {
    this.offsetDistance = window.pageYOffset;
    const sticky = 50;
    const isSticky = window.pageYOffset >= sticky;
    if (store.getState().labbook.isSticky !== isSticky) {
      setStickyDate(isSticky);
    }

    if (isSticky) {
      setMergeMode(false, false);
    }
  }

  /**
    @param {boolean, boolean}
    updates branchOpen state
  */
  @boundMethod
  _toggleBranchesView(branchesOpen, mergeFilter) {
    if (store.getState().containerStatus.status !== 'Running') {
      setMergeMode(branchesOpen, mergeFilter);
    } else {
      setContainerMenuWarningMessage('Stop Project before switching branches. \n Be sure to save your changes.');
    }
  }

  /**
    @param {}
    updates branchOpen state
  */
  _toggleMigrationModal() {
    this.setState({ migrationModalVisible: !this.state.migrationModalVisible });
  }

  /**
    scrolls to top of window
  */
  _scrollToTop() {
    window.scrollTo(0, 0);
  }

  /**
    scrolls to top of window
    @return {boolean, string}
  */
  _getMigrationInfo() {
    const { props, state } = this,
          isOwner = (localStorage.getItem('username') === props.labbook.owner),
          {
            isDeprecated,
            shouldMigrate,
          } = state,
          isPublished = typeof props.labbook.defaultRemote === 'string';

    let migrationText = '';
    let showMigrationButton = false;

    if ((isOwner && isDeprecated && shouldMigrate && isPublished) || (isDeprecated && !isPublished && shouldMigrate)) {
      migrationText = 'This Project needs to be migrated to the latest Project format';
      showMigrationButton = true;
    } else if (!isOwner && isDeprecated && shouldMigrate && isPublished) {
      migrationText = 'This Project needs to be migrated to the latest Project format. The project owner must migrate and sync this project to update.';
    } else if ((isDeprecated && !isPublished && !shouldMigrate) || (isDeprecated && isPublished && !shouldMigrate)) {
      migrationText = 'This project has been migrated. Master is the new primary branch. Old branches should be removed.';
    }

    return { showMigrationButton, migrationText };
  }

  render() {
    const { props, state } = this,
          isLockedBrowser = {
            locked: (props.isPublishing || props.isSyncing || props.isExporting),
            isPublishing: props.isPublishing,
            isExporting: props.isExporting,
            isSyncing: props.isSyncing,
          },
          isLocked = props.isBuilding || props.isSyncing || props.isPublishing || state.isLocked;

    if (props.labbook) {
      const { labbook, branchesOpen } = props,
            branchName = '',
            isDemo = window.location.hostname === Config.demoHostName,
            labbookCSS = classNames({
            Labbook: true,
            'Labbook--detail-mode': props.detailMode,
            'Labbook--branch-mode': branchesOpen,
            'Labbook--demo-mode': isDemo,
            'Labbook--deprecated': state.isDeprecated,
            'Labbook--demo-deprecated': state.isDeprecated && isDemo,
          }),
          deprecatedCSS = classNames({
            Labbook__deprecated: true,
            'Labbook__deprecated--demo': isDemo,
          }),
          { migrationText, showMigrationButton } = this._getMigrationInfo(),
          oldBranches = labbook.branches.filter((branch => branch.branchName.startsWith('gm.workspace') && branch.branchName !== labbook.activeBranchName)),
          migrationModalType = state.migrateComplete ? 'large' : 'large-long';

      return (
        <div className={labbookCSS}>
        <div id="labbook__cover" className="Labbook__cover hidden">
          <Loader/>
        </div>
          <div className="Labbook__spacer flex flex--column">
            {
              state.isDeprecated &&
              <div className={deprecatedCSS}>
                {migrationText}
                <a
                  target="_blank"
                  href="https://docs.gigantum.com/docs/project-migration"
                  rel="noopener noreferrer">
                  Learn More.
                </a>
                {
                  showMigrationButton &&
                  <button
                    className="Labbook__deprecated-action"
                    onClick={() => this._toggleMigrationModal()}
                    disabled={state.migrationInProgress}>
                    Migrate
                  </button>
                }
              </div>
            }
            {
              (state.migrationModalVisible)
              &&
              <Modal
                header="Project Migration"
                handleClose={() => this._toggleMigrationModal()}
                size={migrationModalType}
                renderContent={() => <div className="Labbook__migration-modal">
                  {
                    !state.migrateComplete ?
                    <div className="Labbook__migration-container">
                      <div className="Labbook__migration-content">
                      <p className="Labbook__migration-p"><b>{"Migration will rename the current branch to 'master' and delete all other branches."}</b></p>
                      <p>Before migrating, you should:</p>
                      <ul>
                        <li>
                          Make sure you are on the branch with your latest changes. This is most likely
                          <b style={{ whiteSpace: 'nowrap' }}>
                            {` gm.workspace-${localStorage.getItem('username')}`}
                          </b>
                          . If you just imported this project from a zip file, you should migrate from
                          <b style={{ whiteSpace: 'nowrap' }}>{' gm.workspace'}</b>
                          .
                        </li>
                        <li>Export the project to a zip file as a backup, if desired.</li>
                      </ul>
                      <p>
                        <b>
                          Branch to be migrated:
                        </b>
                        {` ${labbook.activeBranchName}`}
                      </p>
                      <b>Branches to be deleted:</b>
                      {
                        oldBranches.length ?
                        <ul>
                          {
                            oldBranches.map(({ branchName }) => (
                              <li key={branchName}>{branchName}</li>
                            ))
                          }
                        </ul>
                        :
                        <ul>
                          <li>No other branches to delete.</li>
                        </ul>
                      }
                      </div>
                      <div className="Labbook__migration-buttons">
                        <button
                            onClick={() => this._toggleMigrationModal()}
                            className="Btn--flat">
                            Cancel
                        </button>
                        <ButtonLoader
                          buttonState={this.state.buttonState}
                          buttonText="Migrate Project"
                          className=""
                          params={{}}
                          buttonDisabled={false}
                          clicked={() => this._migrateProject()}
                        />
                      </div>
                    </div>
                    :
                    <div className="Labbook__migration-container">
                      <div className="Labbook__migration-content">
                        <div className="Labbook__migration-center">
                        {
                          labbook.defaultRemote ?
                          <Fragment>
                            You should now click
                            <b>{' sync '}</b>
                            to push the new
                            <b>{' master '}</b>
                            branch to the cloud. This is the new primary branch to work from.
                          </Fragment>
                          :
                          <Fragment>
                            Your work has been migrated to the
                            <b>{' master '}</b>
                            branch. This is the new primary branch to work from.
                          </Fragment>
                          }
                          <a
                            target="_blank"
                            href="https://docs.gigantum.com/docs/project-migration"
                            rel="noopener noreferrer">
                            Learn More.
                          </a>
                          <p>Remember to notify collaborators that this project has been migrated. They may need to re-import the project.</p>
                        </div>
                        <div className="Labbook__migration-buttons">
                          <button
                            className="Labbook__migration--dismiss"
                            onClick={() => this._toggleMigrationModal()}>
                            Dismiss
                          </button>
                        </div>
                     </div>
                   </div>
                }
                </div>
                }
              />
            }
            <Header
              {...props}
              description={labbook.description}
              toggleBranchesView={this._toggleBranchesView}
              sectionType={'labbook'}
              containerStatus={labbook.environment.containerStatus}
              imageStatus={labbook.environment.imageStatus}
              isLocked={isLocked}
              collaborators={state.collaborators}
              canManageCollaborators={state.canManageCollaborators}
              visibility={labbook.visibility}
              defaultRemote={labbook.defaultRemote}
              branches={state.branches}
              setBranchUptodate={this._setBranchUptodate}
              isDeprecated={state.isDeprecated}
              updateMigationState={this._updateMigationState}
            />

            <div className="Labbook__routes flex flex-1-0-auto">

              <Switch>
                <Route
                  exact
                  path={`${props.match.path}`}
                  render={() => (
                    <ErrorBoundary type="labbookSectionError">
                      <Overview
                        key={`${props.labbookName}_overview`}
                        labbook={labbook}
                        labbookId={labbook.id}
                        isSyncing={props.isSyncing}
                        isPublishing={props.isPublishing}
                        scrollToTop={this._scrollToTop}
                        sectionType="labbook"
                        history={this.props.history}
                      />
                    </ErrorBoundary>
                        )}
                />

                <Route path={`${props.match.path}/:labbookMenu`}>

                  <Switch>

                    <Route
                      path={`${props.match.path}/overview`}
                      render={() => (

                        <ErrorBoundary
                          type="labbookSectionError"
                          key="overview">
                          <Overview
                               key={`${props.labbookName}_overview`}
                               labbook={labbook}
                               description={labbook.description}
                               labbookId={labbook.id}
                               isSyncing={props.isSyncing}
                               isPublishing={props.isPublishing}
                               scrollToTop={this._scrollToTop}
                               sectionType="labbook"
                                history={this.props.history}
                             />
                        </ErrorBoundary>
                            )}
                    />

                    <Route
                      path={`${props.match.path}/activity`}
                      render={() => (
                        <ErrorBoundary
                          type="labbookSectionError"
                          key="activity">
                          <Activity
                               key={`${props.labbookName}_activity`}
                               labbook={labbook}
                               activityRecords={props.activityRecords}
                               labbookId={labbook.id}
                               branchName={branchName}
                               description={labbook.description}
                               activeBranch={labbook.activeBranchName}
                               isMainWorkspace={branchName === 'master'}
                               sectionType={'labbook'}
                               isLocked={isLocked}
                               isDeprecated={state.isDeprecated}
                               {...props}
                             />
                        </ErrorBoundary>
                          )}
                    />

                    <Route
                      path={`${props.match.url}/environment`}
                      render={() => (
                        <ErrorBoundary
                          type="labbookSectionError"
                          key="environment">
                          <Environment
                               key={`${props.labbookName}_environment`}
                               labbook={labbook}
                               labbookId={labbook.id}
                               containerStatus={this.refs.ContainerStatus}
                               overview={labbook.overview}
                               isLocked={isLocked}
                               {...props}
                             />
                        </ErrorBoundary>)}
                    />

                    <Route
                      path={`${props.match.url}/code`}
                      render={() => (
                        <ErrorBoundary
                          type="labbookSectionError"
                          key="code">
                          <Code
                               labbook={labbook}
                               labbookId={labbook.id}
                               setContainerState={this._setContainerState}
                               isLocked={isLockedBrowser}
                               section={'code'}
                             />

                        </ErrorBoundary>)}
                    />

                    <Route
                      path={`${props.match.url}/inputData`}
                      render={() => (
                        <ErrorBoundary
                          type="labbookSectionError"
                          key="input">
                          <InputData
                               labbook={labbook}
                               labbookId={labbook.id}
                               isLocked={isLockedBrowser}
                               section={'input'}
                             />
                        </ErrorBoundary>)}
                    />

                    <Route
                      path={`${props.match.url}/outputData`}
                      render={() => (
                        <ErrorBoundary
                          type="labbookSectionError"
                          key="output">
                          <OutputData
                               labbook={labbook}
                               labbookId={labbook.id}
                               isLocked={isLockedBrowser}
                               section={'output'}
                             />
                        </ErrorBoundary>)}
                    />

                  </Switch>

                </Route>

              </Switch>

            </div>

          </div>
          <div className="Labbook__veil" />

        </div>);
    }

    if (state.authenticated) {
      return (<Loader />);
    }

    return (<Login auth={props.auth} />);
  }
}

const mapStateToProps = (state, ownProps) => state.labbook;

const mapDispatchToProps = dispatch => ({
  setBuildingState,
});

const LabbookContainer = connect(mapStateToProps, mapDispatchToProps)(Labbook);


const LabbookFragmentContainer = createFragmentContainer(
  LabbookContainer,
  {
    labbook: graphql`
      fragment Labbook_labbook on Labbook {
          id
          description
          defaultRemote
          owner
          name
          creationDateUtc
          visibility
          activeBranchName

          environment{
            containerStatus
            imageStatus
            base{
              developmentTools
            }
          }

          overview{
            remoteUrl
            numAptPackages
            numConda2Packages
            numConda3Packages
            numPipPackages
          }

         branches {
           id
           owner
           name
           branchName
           isActive
           isLocal
           isRemote
         }

          ...Environment_labbook
          ...LabbookOverviewContainer_labbook
          ...LabbookActivityContainer_labbook
          ...Code_labbook
          ...Input_labbook
          ...Output_labbook

      }`,
  },
);

/** *
  * @param {Object} manager
  * data object for reactDND
*/

const backend = (manager) => {
  const backend = HTML5Backend(manager),
    orgTopDropCapture = backend.handleTopDropCapture;

  backend.handleTopDropCapture = (e) => {
    if (backend.currentNativeSource) {
      orgTopDropCapture.call(backend, e);
      backend.currentNativeSource.item.dirContent = getFilesFromDragEvent(e, { recursive: true }); // returns a promise
    }
  };

  return backend;
};

export default DragDropContext(backend)(LabbookFragmentContainer);
