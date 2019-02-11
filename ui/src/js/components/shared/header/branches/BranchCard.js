// vendor
import React, { Component } from 'react';
// components
import DeleteBranch from './DeleteBranch';
import ForceMerge from './ForceMerge';
import ButtonLoader from 'Components/common/ButtonLoader';
// mutations
import WorkonExperimentalBranchMutation from 'Mutations/branches/WorkonExperimentalBranchMutation';
import ResetBranchToRemoteMutation from 'Mutations/branches/ResetBranchToRemoteMutation';
import MergeFromBranchMutation from 'Mutations/branches/MergeFromBranchMutation';
import BuildImageMutation from 'Mutations/BuildImageMutation';
// store
import { setErrorMessage, setInfoMessage } from 'JS/redux/reducers/footer';
import { setContainerMenuWarningMessage } from 'JS/redux/reducers/labbook/environment/environment';
import { setForceCancelRefetch } from 'JS/redux/reducers/labbook/environment/packageDependencies';
import store from 'JS/redux/store';
// assets
import './BranchCard.scss';

export default class BranchCard extends Component {
  constructor(props) {
  	super(props);
    const { owner, labbookName } = store.getState().routes;
    const username = localStorage.getItem('username');
    this.state = {
      owner,
      labbookName,
      username,
      forceMerge: false,
      deleteModalVisible: false,
      showLoader: false,
      forceMergeVisible: false,
      buttonLoaderStateSwitch: '',
      buttonLoaderStateMerge: '',
      buttonLoaderStateReset: '',
    };

    this._merge = this._merge.bind(this);
    this._checkoutBranch = this._checkoutBranch.bind(this);
    this._resetBranch = this._resetBranch.bind(this);
    this._toggleModal = this._toggleModal.bind(this);
    this._handleToggleModal = this._handleToggleModal.bind(this);
  }

  UNSAFE_componentWillReceiveProps(nextProps) {
    if (!nextProps.branchesOpen) {
      this.setState({
        deleteModalVisible: false,
      });
    }
  }
  /**
    @param {}
    checkout branch using WorkonExperimentalBranchMutation
  */
  _checkoutBranch() {
    const self = this;
    const branchName = this.props.name;
    const { owner, labbookName } = this.state;
    const revision = null;
    setInfoMessage(`Checking out ${branchName}`);

    requestAnimationFrame(() => {
      this.setState({
        showLoader: true,
        buttonLoaderStateSwitch: 'loading',
      });
    });

    WorkonExperimentalBranchMutation(
      owner,
      labbookName,
      branchName,
      revision,
      (response, error) => {
        if (error) {
          console.error(error);
          setErrorMessage('Problem Checking out Branch, check if you have a valid session and connection', error);

          self.setState({
            showLoader: false,
            buttonLoaderStateSwitch: 'error',
          });
        } else {
          setForceCancelRefetch(true);
          self.setState({
            showLoader: false,
            buttonLoaderStateSwitch: 'finished',
          });

          setTimeout(() => {
            self.setState({
              buttonLoaderStateSwitch: '',
            });
          }, 3000);

          this.props.setBuildingState(true);

          BuildImageMutation(
            labbookName,
            owner,
            false,
            (response, error) => {
              if (error) {
                console.log(error);
              }
            },
          );
        }
      },
    );
  }
    /**
    @param {}
    checkout branch using WorkonExperimentalBranchMutation
  */
  _resetBranch() {
    const self = this;
    const branchName = this.props.name;
    const { owner, labbookName } = this.state;
    setInfoMessage(`Reseting branch: ${branchName}`);

    requestAnimationFrame(() => {
      this.setState({
        showLoader: true,
        buttonLoaderStateReset: 'loading',
      });
    });

    ResetBranchToRemoteMutation(
      owner,
      labbookName,
      (response, error) => {
        if (error) {
          console.error(error);
          setErrorMessage('Problem Checking out Branch, check if you have a valid session and connection', error);

          self.setState({
            showLoader: false,
            buttonLoaderStateReset: 'error',
          });
          setTimeout(() => {
            self.setState({
              buttonLoaderStateReset: '',
            });
          }, 2000);
        } else {
          setForceCancelRefetch(true);
          self.setState({
            showLoader: false,
            buttonLoaderStateReset: 'finished',
          });

          setTimeout(() => {
            self.setState({
              buttonLoaderStateReset: '',
            });
          }, 3000);

          this.props.setBuildingState(true);

          BuildImageMutation(
            labbookName,
            owner,
            false,
            (response, error) => {
              if (error) {
                console.log(error);
              }
            },
          );
        }
      },
    );
  }
  /**
    @param {Object} params
    merge branch using WorkonExperimentalBranchMutation
  */
  _merge(params) {
    const otherBranchName = this.props.name;
    const { owner, labbookName } = this.state;
    const { activeBranchName } = this.props;
    const { method } = params;
    const self = this;
    setInfoMessage(`Merging ${otherBranchName} into ${activeBranchName}`);
    this.setState({ showLoader: true, buttonLoaderStateMerge: 'loading' });

    MergeFromBranchMutation(
      owner,
      labbookName,
      otherBranchName,
      method,
      (response, error) => {
        if (error) {
          setErrorMessage(`There was a problem merging ${activeBranchName} into ${otherBranchName}`, error);

          if (error[0].message.indexOf('Cannot merge') > -1) {
            self.setState({
              forceMergeVisible: true,
            });
          }

          self.setState({ showLoader: false, buttonLoaderStateMerge: 'error' });
        }
        if (response.mergeFromBranch && response.mergeFromBranch.labbook) {
          setInfoMessage(`${otherBranchName} merged into ${activeBranchName} successfully`);
          self.setState({ showLoader: false, buttonLoaderStateMerge: 'finished' });
        }
        setTimeout(() => {
          self.setState({ buttonLoaderStateMerge: '' });
        }, 3000);

        this.props.setBuildingState(true);

        BuildImageMutation(
          labbookName,
          owner,
          false,
          (response, error) => {
            if (error) {
              console.log(error);
            }
            self.setState({ showLoader: false });
          },
        );
      },
    );
  }
  /**
   * @param {}
   * opens delete branch confirnation modal
   * @return{}
  */
  _toggleModal(name) {
    this.setState({
      [name]: !this.state[name],
    });
  }

  /**
  *  @param {string} modal
  *  passes modal to toggleModal if container is not running
  *  @return {}
  */
  _handleToggleModal(modal) {
    if (store.getState().containerStatus.status !== 'Running') {
      this._toggleModal(modal);
    } else {
      setContainerMenuWarningMessage('Stop Project before deleting branches. \n Be sure to save your changes.');
    }
  }

  /**
  *  @param {string} modal
  *  passes modal to toggleModal if container is not running
  *  @return {}
  */
  _mountModal(ModalJSX) {
    if (store.getState().containerStatus.status !== 'Running') {
      this._toggleModal(modal);
    } else {
      setContainerMenuWarningMessage('Stop Project before deleting branches. \n Be sure to save your changes.');
    }
  }

  render() {
    const { owner, showLoader } = this.state,
      isCurrentBranch = (this.props.name === this.props.activeBranchName),
      branchName = this.props.name,
      showDelete = !isCurrentBranch && (this.props.name !== 'master');

    return (
      <div className="BranchCard Card">
        { isCurrentBranch &&
          <div className="BranchCard--currentBanner">
            CURRENT BRANCH
          </div>

        }
        <h6 className="BranchCard__h6">{branchName}</h6>
        { this.state.deleteModalVisible &&
          <DeleteBranch
            key="BranchDelete__modal"
            branchName={this.props.name}
            cleanBranchName={branchName}
            labbookName={this.state.labbookName}
            labbookId={this.props.labbookId}
            owner={owner}
            toggleModal={this._toggleModal}
          />
        }

        { this.state.forceMergeVisible &&
          <ForceMerge
            key="ForceMerge__modal"
            merge={this._merge}
            toggleModal={this._toggleModal}
          />
        }
        {showDelete &&
          <button
            onClick={() => { this._handleToggleModal('deleteModalVisible'); }}
            className="BranchCard__btn--deleteLabbook button--flat"
          />
        }
        <div className="BranchCard__button">
          {
            isCurrentBranch && this.props.isRemote &&
            <ButtonLoader
              ref="buttonLoaderReset"
              buttonState={this.state.buttonLoaderStateReset}
              buttonText="Reset Branch"
              buttonDisabled={showLoader}
              clicked={this._resetBranch}
            />
          }

          {this.props.mergeFilter &&


            <ButtonLoader
              ref="buttonLoaderMerge"
              buttonState={this.state.buttonLoaderStateMerge}
              params={{ method: null }}
              buttonText="Merge"
              buttonDisabled={showLoader}
              clicked={this._merge}
            />

          }


          {!this.props.mergeFilter &&

            <ButtonLoader
              ref="buttonLoaderSwitch"
              buttonState={this.state.buttonLoaderStateSwitch}
              buttonText="Switch To Branch"
              params={{}}
              buttonDisabled={showLoader || (this.props.name === this.props.activeBranchName)}
              clicked={this._checkoutBranch}
            />

          }
        </div>
        <div
          className="BranchCard__badge"
        >
          {this.props.isRemote ? this.props.isLocal ? 'Local & Remote' : 'Remote' : 'Local'}
        </div>
      </div>
    );
  }
}
