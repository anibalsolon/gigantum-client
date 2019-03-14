// vendor
import React, { Component } from 'react';
import { boundMethod } from 'autobind-decorator';
import classNames from 'classnames';
import { connect } from 'react-redux';
// componenets
import CreateBranch from 'Components/shared/modals/CreateBranch';
import ForceSync from 'Components/shared/modals/ForceSync';
import Branches from 'Components/shared/sidePanel/Branches';
import VisibilityModal from 'Components/shared/modals/VisibilityModal';
import PublishDatasetsModal from 'Components/shared/modals/PublishDatasetsModal';
import LoginPrompt from 'Components/shared/modals/LoginPrompt';
// queries
import UserIdentity from 'JS/Auth/UserIdentity';
import LinkedLocalDatasetsQuery from 'Components/shared/header/actionsSection/queries/LinkedLocalDatasetsQuery';
// store
import { setErrorMessage } from 'JS/redux/reducers/footer';
// utils
import BranchMutations from '../../utils/BranchMutations';
// assets
import './BranchMenu.scss';


/**
  @param {Array} branches
  filters array branhces and return the active branch node
  @return {Object} activeBranch
*/
const extraxtActiveBranch = (branches) => {
   const activeBranch = branches.filter(branch => branch.isActive)[0] || {},
         filteredBranches = branches.filter(branch => !branch.isActive),
         branchMenuList = (filteredBranches.length > 3) ? filteredBranches.slice(0, 3) : filteredBranches,
         otherBranchCount = filteredBranches.length - branchMenuList.length;
   return ({
     activeBranch,
     filteredBranches,
     branchMenuList,
     otherBranchCount,
   });
};

class BranchMenu extends Component {
  state = {
    switchMenuVisible: false,
    createBranchVisible: false,
    branchMutations: new BranchMutations({
      parentId: this.props.sectionId,
      name: this.props.section.name,
      owner: this.props.section.owner,
    }),
    switchingBranch: false,
    sidePanelVisible: false,
    forceSyncModalVisible: false,
    publishModalVisible: false,
    publishDatasetsModalVisible: false,
    publishDatasetsModalAction: 'Publish',
    syncMenuVisible: false,
    showLoginPrompt: false,
    isDataset: this.props.sectionType !== 'labbook',
    action: null,
  };


  /**
    @param {object} nextProps
    @param {object} nextState
    closes sidepanel if isLocked is passed
  */
  static getDerivedStateFromProps(nextProps, nextState) {
    return {
      ...nextState,
      sidePanelVisible: nextProps.isLocked ? false : nextState.sidePanelVisible,
    };
  }

  componentDidMount() {
    window.addEventListener('click', this._closePopups);
  }

  componentWillUnmount() {
    window.removeEventListener('click', this._closePopups);
  }

  /**
    *  @param {}
    *  returns UserIdentityQeury promise
    *  @return {promise}
    */
   @boundMethod
   _checkSessionIsValid() {
    return (UserIdentity.getUserIdentity());
  }
  /**
    @param {}
    calls reset branch on activebranch
  */
  @boundMethod
  _resetBranch() {
    const self = this;
    this._toggleCover('Resetting Branch');
    this.state.branchMutations.resetBranch((response, error) => {
      if (error) {
        setErrorMessage('Failed to reset branch.', error);
      }
      this._toggleCover(null);
      this.props.setBranchUptodate();
    });
    this.setState({ popupVisible: false });
  }
  /**
    @param {Array} branches
    filters array branhces and return the active branch node
    @return {Object} activeBranch
  */
  @boundMethod
  _setModalState(key) {
     const { state } = this;
     const value = !state[key];
     if (!this.props.isLocked && !this.state.isDataset) {
      this.setState({ [key]: value });
     }
  }
  /**
    @param {String} action
    handles labbook cover toggle
    @return {}
  */
  @boundMethod
  _toggleCover(action) {
    if (action) {
      this.setState({ action });
      if (document.getElementById('labbook__cover')) {
        document.getElementById('labbook__cover').classList.remove('hidden');
      }
    } else {
      this.setState({ action: false });
      if (document.getElementById('labbook__cover')) {
        document.getElementById('labbook__cover').classList.add('hidden');
      }
    }
  }
  /**
    @param {Array} branches
    filters array branhces and return the active branch node
    @return {Object} activeBranch
  */
  @boundMethod
  _switchBranch(branch) {
    const { props, state } = this,
          self = this,
          data = {
            branchName: branch.branchName,
          };
      this.setState({
        switchingBranch: branch.branchName,
        switchMenuVisible: false,
      });
      this._toggleCover('Switching Branches');
      state.branchMutations.switchBranch(data, (response, error) => {
        if (error) {
          setErrorMessage('Failed to switch branches.', error);
        }
        self.setState({ switchingBranch: false });
        this._toggleCover(null);
        props.updateMigationState(response);

        state.branchMutations.buildImage((response, error) => {
            if (error) {
              setErrorMessage('Failed to switch branches.', error);
            }
        });
      });
  }
  /**
  *  @param {Boolean} queryForLocalDatasets
  *  @param {Boolean} closePublishDatasetsModal
  *  adds remote url to labbook
  *  @return {string}
  */
  @boundMethod
  _togglePublishModal(queryForLocalDatasets, closePublishDatasetsModal) {
    if (this.props.isExporting) {
      setWarningMessage('Publishing is currently only available on the main workspace branch.');
      this.setState({ publishWarningVisible: true });
    } else if (queryForLocalDatasets && typeof queryForLocalDatasets === 'boolean') {
      LinkedLocalDatasetsQuery.getLocalDatasets({ owner: this.props.section.owner, name: this.props.section.name }).then((res) => {
          const localDatasets = res.data && res.data.labbook.linkedDatasets.filter(linkedDataset => linkedDataset.defaultRemote && linkedDataset.defaultRemote.slice(0, 4) !== 'http');
          if (localDatasets.length === 0) {
            this.setState({ publishModalVisible: !this.state.publishModalVisible });
          } else {
            this.setState({ localDatasets, publishDatasetsModalVisible: !this.state.publishDatasetsModalVisible, publishDatasetsModalAction: 'Publish' });
          }
      });
    } else if (closePublishDatasetsModal) {
      this.setState({ publishDatasetsModalVisible: !this.state.publishDatasetsModalVisible });
    } else {
      this.setState({ publishModalVisible: !this.state.publishModalVisible });
    }
  }

  /**
  *  @param {}
  *  resets state after publish
  *  @return {}
  */
  @boundMethod
  _resetState() {
    this.setState({
      remoteUrl: '',
      showLoginPrompt: true,
    });
  }

  /**
  *  @param {}
  *  resets state after publish
  *  @return {}
  */
  @boundMethod
  _resetPublishState(publishDisabled) {
    this.setState({
      menuOpen: false,
      publishDisabled,
    });
  }
  /**
    @param {} -
    sets state to toggle the switch dropdown
    @return {}
  */
  @boundMethod
  _toggleBranchSwitch() {
    if (!this.props.isLocked && !this.state.isDataset) {
      const { state } = this;
      this.setState({ switchMenuVisible: !state.switchMenuVisible });
    }
  }

  /**
    @param {} -
    sets state to toggle the switch dropdown
    @return {}
  */
  @boundMethod
  _closePopups(evt) {
     const { state } = this;
     if (evt.target.className.indexOf('BranchMenu') < 0) {
       this.setState({
         switchMenuVisible: false,
         syncMenuVisible: false,
       });
     }
  }

  /**
    @param {} -
    sets state to toggle the switch dropdown
    @return {}
  */
  @boundMethod
  _toggleSidePanel(sidePanelVisible) {
      if (!this.props.isLocked && !this.state.isDataset) {
        this.setState({ sidePanelVisible, switchMenuVisible: false });
      }
  }

  /**
  *  @param {}
  *  closes login prompt modal
  *  @return {}
  */
  @boundMethod
  _closeLoginPromptModal() {
    this.setState({ showLoginPrompt: false });
  }
  /**
  *  @param {Boolean} - commitsHovered
  *  sets hoverstate for committs
  *  @return {}
  */
  @boundMethod
  _hovercommits(commitsHovered) {
    this.setState({ commitsHovered });
  }
  /**
  *  @param {Boolean} blockReset
  *  toggles reset popup
  *  @return {}
  */
  @boundMethod
  _toggleResetPopup(blockReset) {
    if (!blockReset) {
      this.setState({ popupVisible: !this.state.popupVisible });
    }
  }
  /**
    @param {Boolean} - disableDropdown
    sets state to toggle the switch dropdown
    @return {}
  */
  @boundMethod
  _toggleSyncDropdown(disableDropdown) {
    if (!disableDropdown) {
      const { state } = this;
      this.setState({ syncMenuVisible: !state.syncMenuVisible });
    }
  }
  /**
  *  @param {}
  *  resets state after publish
  *  @return {}
  */
  @boundMethod
  _setRemoteSession() {
    this.setState({
      addedRemoteThisSession: true,
      remoteUrl: `https://gigantum.com/${this.state.owner}/${this.state.labbookName}`,
    });
  }

  /**
  *  @param {Object} - activeBranch
  *  determines whether or not user has write access
  *  @return {}
  */
  @boundMethod
  _hasWriteAccess(activeBranch) {
    const { props } = this;
    const username = localStorage.getItem('username');

    if (!props.collaborators || (props.collaborators && !props.collaborators[props.section.name])) {
      return false;
    } else {
      const filteredArr = props.collaborators[props.section.name].filter(collaborator => collaborator.collaboratorUsername === username);
      if (filteredArr.length === 0) {
        return false;
      } else if ((filteredArr[0].permission === 'READ_ONLY') || ((filteredArr[0].permission === 'READ_WRITE') && (activeBranch.branchName === 'master'))) {
        return false;
      } else {
        return true;
      }
    }
  }
  /**
  *  @param {Boolean} - pullOnly
  *  @param {Boolean} - allowSync
  *  @param {Boolean} - allowSyncPull
  *  @param {Function} - passedSuccessCall
  *  handles syncing or publishing the project
  *  @return {}
  */
  @boundMethod
  _handleSyncButton(pullOnly, allowSync, allowSyncPull, passedSuccessCall) {
    this.setState({ syncMenuVisible: false });
    if (allowSync || (pullOnly && allowSyncPull)) {
      if (!this.props.defaultRemote) {
        this._togglePublishModal(!this.state.isDataset, false);
      } else {
        const self = this;
        const data = {
            successCall: () => {
              this.props.setSyncingState(false);
              if (this.props.sectionType === 'labbook') {
                this.state.branchMutations.buildImage((response, error) => {
                  if (error) {
                    console.error(error);

                    setMultiInfoMessage(id, `ERROR: Failed to build ${this.props.section.name}`, null, true, error);
                  }
                });
                this.props.setBranchUptodate();
              }
            },
            failureCall: (errorMessage) => {
              this.props.setSyncingState(false);
              if ((errorMessage.indexOf('MergeError') > -1) || (errorMessage.indexOf('Cannot merge') > -1) || (errorMessage.indexOf('Merge conflict') > -1)) {
                self._toggleSyncModal();
                this.setState({ pullOnly });
              }
            },
            pullOnly: pullOnly || false,
          };

        this._checkSessionIsValid().then((response) => {
          if (!navigator.onLine) {
            self.setState({ showLoginPrompt: true });
          } else if (!(response.data && response.data.userIdentity && response.data.userIdentity.isSessionValid)) {
            this.props.auth.renewToken(true, () => {
              self.setState({ showLoginPrompt: true });
            }, () => {
              self.handleSyncButton(pullOnly, allowSync, allowSyncPull);
            });
          } else if (this.props.sectionType !== 'labbook') {
            this.state.branchMutations.syncDataset(data, (response, error) => {
              if (error) {
                data.failureCall(error);
              }
            });
          } else {
            LinkedLocalDatasetsQuery.getLocalDatasets({ owner: this.props.section.owner, name: this.props.section.name }).then((res) => {
              const localDatasets = res.data && res.data.labbook.linkedDatasets.filter(linkedDataset => linkedDataset.defaultRemote && linkedDataset.defaultRemote.slice(0, 4) !== 'http');
              if ((localDatasets.length === 0) || pullOnly) {
                this.props.setSyncingState(true);

                this.state.branchMutations.syncLabbook(data, (response, error) => {
                  if (error) {
                    data.failureCall(error);
                  }
                  if (passedSuccessCall) {
                    passedSuccessCall();
                  }
                });
              } else {
                this.setState({ localDatasets, publishDatasetsModalVisible: !this.state.publishDatasetsModalVisible, publishDatasetsModalAction: 'Sync' });
              }
          });
          }
        });
      }
    }
  }

      /**
    *  @param {Object} activeBranch
    *  @param {Boolean} hasWriteAccess
    *  @param {Boolean} upToDate
    *  returns tooltip info
    *  @return {string}
    */
    @boundMethod
    _getTooltipText(activeBranch, hasWriteAccess, upToDate) {
      const { props, state } = this;
      const { collaborators } = props;
      const sectionCollabs = collaborators && collaborators[props.section.name] || null;
      const defaultDatasetMessage = 'Datasets does not currently support branching features';
      const isPullOnly = props.defaultRemote && !hasWriteAccess && sectionCollabs;
      const syncOrPublish = props.defaultRemote ? isPullOnly ? 'Pull' : 'Sync' : 'Publish';
      return {
        syncTooltip: props.isLocked ? `Cannot ${syncOrPublish} while Project is in use` : (activeBranch.branchName !== 'master' && !props.defaultRemote) ? 'Must publish Master branch first' : !props.defaultRemote ? 'Publish' : props.defaultRemote && !sectionCollabs ? 'Please wait while Project data is being fetched' : !hasWriteAccess ? 'Pull' : 'Sync',
        manageTooltip: props.isLocked ? 'Cannot Manage Branches while Project is in use' : state.isDataset ? defaultDatasetMessage : 'Manage Branches',
        createTooltip: props.isLocked ? 'Cannot Create Branch while Project is in use' : state.isDataset ? defaultDatasetMessage : 'Create Branch',
        resetTooltip: state.isDataset ? defaultDatasetMessage : props.isLocked ? 'Cannot Reset Branch while Project is in use' : !activeBranch.isRemote ? 'Branch must be remote' : activeBranch.commitsAhead === undefined ? 'Please wait while branch data is being fetched' : upToDate ? 'Branch up to date' : 'Reset Branch to Remote',
        switchTooltip: props.isLocked ? 'Cannot switch branches while Project is in use' : state.isDataset ? defaultDatasetMessage : '',
        commitTooltip: `${activeBranch.commitsBehind ? `${activeBranch.commitsBehind} Commits Behind, ` : ''} ${activeBranch.commitsAhead ? `${activeBranch.commitsAhead} Commits Ahead` : ''}`,
      };
    }

    /**
    *  @param {}
    *  toggles sync modal
    *  @return {string}
    */
   @boundMethod
    _toggleSyncModal() {
      this.setState({ forceSyncModalVisible: !this.state.forceSyncModalVisible, publishDatasetsModalVisible: false });
    }

  render() {
    const { props, state } = this,
          { branches } = props,
          branchMenuCSS = classNames({
            BranchMenu: true,
            hidden: props.isSticky,
          }),
          {
            activeBranch,
            filteredBranches,
            branchMenuList,
            otherBranchCount,
          } = extraxtActiveBranch(branches),
          { collaborators } = props,
          sectionCollabs = collaborators && collaborators[props.section.name] || null,
          waitingOnCollabs = !sectionCollabs,
          hasWriteAccess = this.props.defaultRemote ? this._hasWriteAccess(activeBranch) : true,
          upToDate = activeBranch.commitsAhead === 0 && activeBranch.commitsBehind === 0,
          allowSync = !((activeBranch.branchName !== 'master') && !this.props.defaultRemote) && !props.isLocked && hasWriteAccess,
          allowSyncPull = !((activeBranch.branchName !== 'master') && !this.props.defaultRemote) && !props.isLocked && props.defaultRemote,
          allowReset = !props.isLocked && !upToDate && activeBranch.isRemote && (activeBranch.commitsAhead !== undefined),
          statusText = activeBranch.isRemote ? 'Local & Remote' : 'Local only',
          showPullOnly = props.defaultRemote && !hasWriteAccess && !waitingOnCollabs,
          disableDropdown = !allowSyncPull || !props.defaultRemote || showPullOnly,
          {
            syncTooltip,
            manageTooltip,
            createTooltip,
            resetTooltip,
            switchTooltip,
            commitTooltip,
          } = this._getTooltipText(activeBranch, hasWriteAccess, upToDate),
          syncButtonText = props.defaultRemote ? showPullOnly ? 'Pull' : 'Sync' : 'Publish',
          switchDropdownCSS = classNames({
            'BranchMenu__dropdown-menu': true,
            hidden: !state.switchMenuVisible,
          }),
          drodownButtonCSS = classNames({
            'BranchMenu__dropdown-btn': true,
            'BranchMenu__dropdown-btn--disabled': props.isLocked || state.isDataset,
            'BranchMenu__dropdown-btn--open': state.switchMenuVisible,
            'Tooltip-data Tooltip-data': props.isLocked || state.isDataset,
          }),
          branchNameCSS = classNames({
            'BranchMenu__branch-name': !state.switchingBranch,
            hidden: state.switchingBranch,
          }),
          branchSwitchingNameCSS = classNames({
            'BranchMenu__branch-name BranchMenu__branch-name--switching': state.switchingBranch,
            hidden: !state.switchingBranch,
          }),
          syncMenuDropdownCSS = classNames({
            'BranchMenu__dropdown-menu': state.syncMenuVisible && !disableDropdown,
            hidden: !state.syncMenuVisible,
          }),
          syncMenuDropdownButtonCSS = classNames({
            'BranchMenu__btn BranchMenu__btn--sync-dropdown': true,
            'BranchMenu__btn--sync-dropdown--disabled': disableDropdown,
            'BranchMenu__btn--sync-open': state.syncMenuVisible,
          }),
          syncCSS = classNames({
            'BranchMenu__btn BranchMenu__btn--sync': true,
            'BranchMenu__btn--sync--publish': !props.defaultRemote,
            'BranchMenu__btn--sync--pull': showPullOnly,
            'BranchMenu__btn--sync--upToDate': props.defaultRemote && (upToDate || (activeBranch.commitsAhead === undefined)) && !showPullOnly,
            'BranchMenu__btn--sync--pull--disabled': showPullOnly && !allowSyncPull,
            'BranchMenu__btn--sync--publish--disabled': !props.defaultRemote && !allowSync,
            'BranchMenu__btn--sync--upToDate--disabled': props.defaultRemote && !allowSync && !showPullOnly,
            'Tooltip-data': !state.commitsHovered,
          }),
          manageCSS = classNames({
            'BranchMenu__btn BranchMenu__btn--manage': true,
            'BranchMenu__btn--manage--disabled': props.isLocked || state.isDataset,
            'Tooltip-data': true,
          }),
          resetCSS = classNames({
            'BranchMenu__btn BranchMenu__btn--reset': true,
            'BranchMenu__btn--reset--disabled': !allowReset || state.isDataset,
            'Tooltip-data': true,
          }),
          createCSS = classNames({
            'BranchMenu__btn BranchMenu__btn--create': true,
            'BranchMenu__btn--create--disabled': props.isLocked || state.isDataset,
            'Tooltip-data': true,
          }),
          popupCSS = classNames({
            BranchMenu__popup: true,
            hidden: !this.state.popupVisible,
          });

    return (
      <div className={branchMenuCSS}>
          <div className="BranchMenu__dropdown">
                <div
                onClick={() => this._toggleBranchSwitch() }
                data-tooltip={switchTooltip}
                className={drodownButtonCSS}>
                  <div className={branchNameCSS}>
                    <div className="BranchMenu__dropdown-label">Branch:</div>
                    <div className="BranchMenu__dropdown-text">{activeBranch.branchName}</div>
                  </div>

                  <div className={branchSwitchingNameCSS}>
                    <span className="BranchMenu__dropdown-label">Branch:</span>
                    <span className="BranchMenu__dropdown-text ">
                      {`switching to ${state.switchingBranch}...`}
                    </span>
                  </div>
                  <div
                    className="BranchMenu__status Tooltip-data Tooltip-data--small"
                    data-tooltip={statusText}>
                    {
                      activeBranch.isLocal ?
                      <div className="BranchMenu__status--local"></div>
                      :
                      <div></div>
                    }
                    {
                      activeBranch.isRemote ?
                      <div className="BranchMenu__status--remote"></div>
                      :
                      <div></div>
                    }
                  </div>
                </div>
                <div className={switchDropdownCSS}>
                  <h5 className="BranchMenu__h5">Quick Switch</h5>
                  <ul className="BranchMenu__ul">
                    {
                      branchMenuList.map((branch) => {
                        const cloudIconCSS = classNames({
                            BranchMenu__icon: true,
                            'BranchMenu__icon--cloud': branch.isRemote,
                            'BranchMenu__icon--empty': !branch.isRemote,
                          }),
                          localIconCSS = classNames({
                            BranchMenu__icon: true,
                            'BranchMenu__icon--local': branch.isLocal,
                            'BranchMenu__icon--empty': !branch.isLocal,
                          });

                        return (<li
                            onClick={ () => this._switchBranch(branch) }
                            key={branch.branchName}
                            className="BranchMenu__list-item">
                            <div className="BranchMenu__text">{branch.branchName}</div>
                            <div className="BranchMenu__icons">
                              <div className={cloudIconCSS}></div>
                              <div className={localIconCSS}></div>
                            </div>
                          </li>);
                      })
                    }

                    {
                      (otherBranchCount > 0)
                      && <div className="BranchMenu__other-text">{`+${otherBranchCount} others` }</div>
                    }

                    { (filteredBranches.length === 0)
                      &&
                      <li
                        className="BranchMenu__list-item BranchMenu__list-item--create"
                        onClick={() => this._setModalState('createBranchVisible') }
                      >
                        No other branches.
                        <button
                          className="Btn--flat"
                        >
                          Create a new branch?
                        </button>
                      </li>
                    }
                  </ul>
                  <div className="BranchMenu__menu-button">
                    <button
                      onClick={() => this._toggleSidePanel(true)}
                      className="BranchMenu__button Btn--flat">
                        Manage Branches
                    </button>
                  </div>
                </div>
          </div>
          {
          !this.state.action ?
          <div className="BranchMenu__buttons">
            <button
              onClick={() => this._toggleSidePanel(true)}
              className={manageCSS}
              data-tooltip={manageTooltip}
              type="Submit">
            </button>
            <button
              className={createCSS}
              type="Submit"
              data-tooltip={createTooltip}
              onClick={() => this._setModalState('createBranchVisible') }>
            </button>
            <div className="BranchMenu__reset-container">
              <button
                className={resetCSS}
                type="Submit"
                data-tooltip={resetTooltip}
                onClick={() => this._toggleResetPopup(!allowReset || state.isDataset)}
                >
              </button>
              <div className={popupCSS}>
                <p>You are about to reset this branch. Resetting a branch will get rid of local changes. Click 'Confirm' to proceed.</p>
                <div className="flex justify--space-around">
                  <button
                    className="Btn--flat"
                    onClick={(evt) => { this._toggleResetPopup() }}
                    >
                      Cancel
                    </button>
                  <button
                    className="BranchMenu__reset-confirm"
                    onClick={() => this._resetBranch()}
                  >
                    Confirm
                  </button>
                </div>
              </div>
            </div>
            <div className="BranchMenu__sync-container">
              <button
                className={syncCSS}
                onClick={() => { this._handleSyncButton(showPullOnly, allowSync, allowSyncPull); }}
                data-tooltip={syncTooltip}
                type="Submit">
                {
                  !upToDate && allowSync && (activeBranch.commitsAhead !== undefined) &&
                  <div
                    className="BranchMenu__sync-status Tooltip-data Tooltip-data--small"
                    data-tooltip={commitTooltip}
                    onMouseEnter={() => this._hovercommits(true)}
                    onMouseLeave={() => this._hovercommits(false)}
                  >
                    {
                      (activeBranch.commitsBehind !== 0) &&
                      <div className="BranchMenu__sync-status--commits-behind">{ activeBranch.commitsBehind }</div>
                    }
                    {
                      activeBranch.commitsAhead !== 0 &&
                      <div className="BranchMenu__sync-status--commits-ahead">{ activeBranch.commitsAhead }</div>
                    }
                  </div>
                }
                <div
                  className="BranchMenu__btn--text"
                >
                  {syncButtonText}
                </div>
              </button>

              <button
                className={syncMenuDropdownButtonCSS}
                onClick={() => { this._toggleSyncDropdown(disableDropdown); }}
                type="Submit">
              </button>

              <div className={syncMenuDropdownCSS}>
                <h5 className="BranchMenu__h5">Remote Action</h5>
                <ul className="BranchMenu__ul">
                  {
                    allowSync &&
                    <li
                      className="BranchMenu__list-item"
                      onClick={() => this._handleSyncButton(false, allowSync, allowSyncPull)}>
                      Sync (Pull then Push)
                    </li>
                  }
                  <li
                    className="BranchMenu__list-item"
                    onClick={() => this._handleSyncButton(true, allowSync, allowSyncPull)}>
                      Pull (Pull-only)
                  </li>
                </ul>
              </div>

            </div>
          </div>
          :
          <div className="BranchMenu__action">{state.action}</div>
          }

          <CreateBranch
            modalVisible={state.createBranchVisible}
            description={props.section.description}
            toggleModal={this._setModalState}
          />

          <Branches
            sidePanelVisible={state.sidePanelVisible}
            toggleSidePanel={this._toggleSidePanel}
            defaultRemote={props.defaultRemote}
            branches={props.branches}
            disableDropdown={disableDropdown}
            activeBranch={activeBranch}
            toggleModal={this._setModalState}
            isSticky={props.isSticky}
            branchMutations={state.branchMutations}
            isLocked={props.isLocked}
            handleSyncButton={this._handleSyncButton}
            waitingOnCollabs={waitingOnCollabs}
            allowSync={allowSync}
            allowSyncPull={allowSyncPull}
            sectionId={props.sectionId}
            syncTooltip={syncTooltip}
            switchBranch={this._switchBranch}
            toggleCover={this._toggleCover}
            isDeprecated={props.isDeprecated}
            setBranchUptodate={this.props.setBranchUptodate}
            showPullOnly={showPullOnly}
          />
          {
          state.publishModalVisible &&

          <VisibilityModal
            owner={props.section.owner}
            labbookName={props.section.name}
            labbookId={props.sectionId}
            remoteUrl={props.defaultRemote}
            auth={props.auth}
            buttonText="Publish"
            header="Publish"
            modalStateValue="visibilityModalVisible"
            sectionType={props.sectionType}
            setPublishingState={props.setPublishingState}
            checkSessionIsValid={this._checkSessionIsValid}
            toggleModal={this._togglePublishModal}
            resetState={this._resetState}
            resetPublishState={this._resetPublishState}
            setRemoteSession={this._setRemoteSession}
          />

        }
        {
          state.publishDatasetsModalVisible &&

          <PublishDatasetsModal
            owner={props.section.owner}
            labbookName={props.section.name}
            labbookId={props.sectionId}
            remoteUrl={props.remoteUrl}
            auth={props.auth}
            buttonText="Publish All"
            header={state.publishDatasetsModalAction}
            pullOnly={state.pullOnly}
            modalStateValue="visibilityModalVisible"
            sectionType={props.sectionType}
            setSyncingState={props.setSyncingState}
            setPublishingState={props.setPublishingState}
            toggleSyncModal={this._toggleSyncModal}
            checkSessionIsValid={this._checkSessionIsValid}
            toggleModal={this._togglePublishModal}
            resetState={this._resetState}
            resetPublishState={this._resetPublishState}
            setRemoteSession={this._setRemoteSession}
            handleSync={this._handleSyncButton}
            localDatasets={state.localDatasets || []}
          />

        }
        {
          state.forceSyncModalVisible &&

          <ForceSync
            toggleSyncModal={this._toggleSyncModal}
            sectionType={props.sectionType}
            pullOnly={state.pullOnly}
          />
        }
        {
          state.showLoginPrompt &&

          <LoginPrompt closeModal={this._closeLoginPromptModal} />
        }
      </div>
    );
  }
}


const mapStateToProps = (state, ownProps) => ({
  collaborators: state.collaborators.collaborators,
});

const mapDispatchToProps = dispatch => ({
});

export default connect(mapStateToProps, mapDispatchToProps)(BranchMenu);
