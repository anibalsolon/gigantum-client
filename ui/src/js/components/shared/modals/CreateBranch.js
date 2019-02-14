// vendor
import React, { Component, Fragment } from 'react';
import dateFormat from 'dateformat';
import Moment from 'moment';
import classNames from 'classnames';
// Mutations
import CreateExperimentalBranchMutation from 'Mutations/branches/CreateExperimentalBranchMutation';
// components
import ButtonLoader from 'Components/common/ButtonLoader';
import Modal from 'Components/common/Modal';
// utilities
import validation from 'JS/utils/Validation';
import BuildImageMutation from 'Mutations/container/BuildImageMutation';
// store
import { setErrorMessage } from 'JS/redux/reducers/footer';
import store from 'JS/redux/store';
// assets
import './CreateBranch.scss';

export default class CreateBranchModal extends Component {
  constructor(props) {
    super(props);
    const formatedCurrentTimestamp = Moment().format('M/DD/YY h:mm:ss A');
    const formatedTimestamp = props.selected ? Moment(Date.parse(props.selected.activityNode.timestamp)).format('M/DD/YY h:mm:ss A') : '';
    this.state = {
      modalVisible: props.modalVisible,
      showLoginPrompt: false,
      textWarning: 'hidden',
      textLength: 0,
      showError: false,
      branchName: '',
      branchDescription: props.selected ? `${props.selected.description}. ${props.selected.activeBranch} at ${formatedTimestamp}.` : props.description ? props.description : '',
      createButtonClicked: false,
      buttonLoaderCreateBranch: '',
    };

    this._showModal = this._showModal.bind(this);
    this._hideModal = this._hideModal.bind(this);
    this._createNewBranch = this._createNewBranch.bind(this);
    this._updateTextState = this._updateTextState.bind(this);
  }


  UNSAFE_componentWillReceiveProps(nextProps) {
    const { state } = this;
    if (nextProps.modalVisible !== state.modalVisible) {
      this.setState({ modalVisible: nextProps.modalVisible });
    }

    if (nextProps.selected) {
      const formattedTimestamp = Moment(Date.parse(nextProps.selected.timestamp)).format('YYYYMMDD-HHmmss');
      const branchName = `rollback-to-${formattedTimestamp}`;
      this.setState({ branchName });
    } else {
      this.setState({ branchName: '' });
    }
  }

  /**
  *   @param {}
  *   shows modal by setting state
  *   @return {}
  */
  _showModal() {
    this.setState({ modalVisible: true });
  }

  /**
  *   @param {}
  *   hides modal by stetting state
  *   @return {}
  */
  _hideModal(inputsDisabled) {
    const { props } = this;
    if (!inputsDisabled) {
      this.setState({ modalVisible: false });

      if (props.toggleModal) {
        props.toggleModal('createBranchVisible');
      }
    }
  }

  /**
  *   @param {event,string} evt, key
  *   returns error text when a branch name is invalid
  *   @return {}
  */
  _getErrorText() {
    const { state } = this;
    return state.errorType === 'send' ? 'Error: Last character cannot be a hyphen.' : 'Error: Branch name may only contain lowercase alphanumeric and `-`. (e.g. new-branch-name)';
  }

  /**
  *   @param {event,string} evt, key
  *   sets state of text using a key
  *   @return {}
  */
  _updateTextState = (evt, key) => {
    const state = {};

    if (key === 'branchName') {
      const isMatch = validation.labbookName(evt.target.value);
      if (isMatch) {
        this.setState({
          branchName: evt.target.value,
          errorType: '',
          showError: false,
        });
      } else {
        this.setState({
          showError: ((isMatch === false) && (evt.target.value.length > 0)),
          errorType: '',
        });
      }
    } else {
      state[key] = evt.target.value;
    }

    const textLength = 240 - evt.target.value.length;
    if (textLength >= 100) {
      state.textWarning = 'CreateBranch__warning--hidden';
    } else if ((textLength <= 100) && (textLength > 50)) {
      state.textWarning = 'CreateBranch__warning--green';
    } else if ((textLength <= 50) && (textLength > 20)) {
      state.textWarning = 'CreateBranch__warning--yellow';
    } else {
      state.textWarning = 'CreateBranch__warning--red';
    }
    state.textLength = textLength;

    this.setState(state);
  }

  /**
  *   @param {}
  *   formats date for branch name
  *   @return {}
  */
  _formattedISO(date) {
    return dateFormat(date, 'isoDateTime').toLowerCase().replace(/:/g, '-');
  }

  /**
  *   @param {}
  *   triggers CreateExperimentalBranchMutation
  *   @return {}
  */
  _createNewBranch() {
    const self = this,
          { state, props } = this,
          { owner, labbookName } = store.getState().routes,
          { branchName } = this.state,
          revision = props.selected ? props.selected.commit : null;


    this.setState({ buttonLoaderCreateBranch: 'loading' });

    CreateExperimentalBranchMutation(
      owner,
      labbookName,
      branchName,
      revision,
      state.branchDescription,
      (response, error) => {
        if (error) {
          setErrorMessage('Problem Creating new branch', error);

          setTimeout(() => {
            this.setState({ buttonLoaderCreateBranch: 'error' });
          }, 1000);
        } else {
          if (props.selected) {
            props.setBuildingState(true);
            BuildImageMutation(
              owner,
              labbookName,
              false,
              (response, error) => {
                if (error) {
                  setErrorMessage(`${labbookName} failed to build`, error);
                }

                return 'finished';
              },
            );
          }

          this.setState({ buttonLoaderCreateBranch: 'finished' });
        }

        setTimeout(() => {
          this.setState({ buttonLoaderCreateBranch: '' });

          if (self._hideModal) {
            self._hideModal();
          }
        }, 2000);
      },
    );
  }

  render() {
    const { props, state } = this,
          createDisabled = state.showError || (state.branchName.length === 0) || state.createButtonClicked,
          inputsDisabled = state.buttonLoaderCreateBranch !== '',
          formatedCurrentTimestamp = Moment().format('MM/DD/YY hh:mm:ss A'),
          formatedTimestamp = props.selected ? Moment(Date.parse(props.selected.activityNode.timestamp)).format('M/DD/YY h:mm:ss A') : '',
          branchNameTimestamp = props.selected ? Moment(Date.parse(props.selected.activityNode.timestamp)).format('MMDDYY-HHmmss').toLowerCase() : '',
          branchDefault = props.selected ? `${props.selected.activeBranch}-at-${branchNameTimestamp}` : '',
          textAreaDefault = props.selected ? `${props.selected.description} (from ${props.selected.activeBranch} at ${formatedTimestamp})` : props.description ? props.description : '',
          inputCSS = classNames({
            'CreateBranch__input--invalid': state.showError,
          }),
          errorCSS = classNames({
            CreateBranch__error: state.showError,
            hidden: !state.showError,
          }),
          branchModalTitle = props.selected ? 'Create Rollback Branch' : 'Create Branch',
          icon = props.selected ? 'rollback' : 'create';


    return (
      <div>
        { state.modalVisible
          && <Modal
          handleClose={() => { this._hideModal(inputsDisabled); }}
          size="large"
          header={branchModalTitle}
          icon={icon}
          renderContent={() => (<div className="CreateBranch">
            <div>
              <label>Name</label>
              <input
                type="text"
                maxLength="80"
                className={inputCSS}
                onChange={evt => this._updateTextState(evt, 'branchName')}
                onKeyUp={evt => this._updateTextState(evt, 'branchName')}
                placeholder="Enter a unique branch name"
                defaultValue={branchDefault}
                disabled={inputsDisabled}
              />
              <span className={errorCSS}>{this._getErrorText()}</span>
            </div>

            <div>
              <label>Description</label>
              <textarea
                className="CreateBranch__input--description"
                disabled={inputsDisabled}
                onChange={evt => this._updateTextState(evt, 'branchDescription')}
                onKeyUp={evt => this._updateTextState(evt, 'branchDescription')}
                maxLength="240"
                placeholder="Briefly describe this branch, its purpose and any other key details. "
                defaultValue={textAreaDefault}
              />
              <p className={`CreateBranch__warning ${state.textWarning}`}>{`${state.textLength} characters remaining`}</p>
            </div>

            <div className="CreateBranch_nav">
              <div className="CreateBranch__navGroup">
                <div className="CreateBranch_navItem">
                  <button
                    type="submit"
                    disabled={inputsDisabled}
                    onClick={() => { this._hideModal(); }}
                    className="CreateBranch__btn--progress button--flat">
                    Cancel
                  </button>
                </div>

                <div className="CreateBranch_navItem">
                  <ButtonLoader
                    ref="buttonLoaderCreateBranch"
                    buttonState={state.buttonLoaderCreateBranch}
                    buttonText="Create"
                    params={{}}
                    buttonDisabled={createDisabled}
                    clicked={this._createNewBranch}
                  />
                </div>
              </div>
            </div>
          </div>)
         }/>
        }
      </div>

    );
  }
}
