import { QueryRenderer, graphql } from 'react-relay';
import React, { Component } from 'react';
import classNames from 'classnames';
import { connect } from 'react-redux';
// environment
import environment from 'JS/createRelayEnvironment';
// store
import store from 'JS/redux/store';
import { setCollaborators, setCanManageCollaborators } from 'JS/redux/reducers/labbook/branchMenu/collaborators/collaborators';
// components
import CollaboratorsModal from './CollaboratorsModal';
// assets
import './Collaborators.scss';

export const CollaboratorsQuery = graphql`
  query CollaboratorsQuery($name: String!, $owner: String!){
    labbook(name: $name, owner: $owner){
      collaborators
      canManageCollaborators
    }
  }`;

export const CollaboratorsDatasetQuery = graphql`
query CollaboratorsDatasetQuery($name: String!, $owner: String!){
  dataset(name: $name, owner: $owner){
    collaborators
    canManageCollaborators
  }
}`;


class CollaboratorButton extends Component {
  constructor(props) {
    	super(props);
    	this.state = {
      collaboratorModalVisible: false,
      canClickCollaborators: false,
      sessionValid: true,
    };

    this._toggleCollaborators = this._toggleCollaborators.bind(this);
  }

  static getDerivedStateFromProps(nextProps, nextState) {
    if (nextProps.menuOpen) {
      return nextProps.checkSessionIsValid().then((res) => {
        if (res.data && res.data.userIdentity && res.data.userIdentity.isSessionValid) {
          return {
            ...nextState,
            sessionValid: true,
          };
        }
        return {
          ...nextState,
          sessionValid: false,
        };
      });
    }
    return nextState;
  }

  componentDidMount() {
    this.props.setCollaborators({ [this.props.labbookName]: this.collaborators });
    this.props.setCanManageCollaborators({ [this.props.labbookName]: this.canManageCollaborators });
  }

  _toggleCollaborators() {
    if (navigator.onLine) {
      if (this.state.sessionValid) {
        this.setState({ collaboratorModalVisible: !this.state.collaboratorModalVisible });
      } else {
        this.props.auth.renewToken(true, () => {
          this.props.showLoginPrompt();
        }, () => {
          this.setState({ collaboratorModalVisible: !this.state.collaboratorModalVisible });
        });
      }
    } else {
      this.props.showLoginPrompt();
    }
  }

  _getCollaboratorList(collaborators, collaboratorFilteredArr) {
    let lastParsedIndex;
    let collaboratorSubText = collaboratorFilteredArr ? collaboratorFilteredArr.join(', ') : '';

    if (collaboratorSubText.length > 18 && collaboratorSubText.length) {
      collaboratorSubText = collaboratorSubText.slice(0, 18);

      lastParsedIndex = collaboratorSubText.split(', ').length - 1;

      const lastParsed = collaboratorSubText.split(', ')[lastParsedIndex];

      if (collaborators[lastParsedIndex] !== lastParsed) {
        lastParsedIndex--;

        collaboratorSubText = collaboratorSubText.split(', ');
        collaboratorSubText.pop();
        collaboratorSubText = collaboratorSubText.join(', ');
      }
      const collaboratorLength = collaboratorFilteredArr.length - lastParsedIndex - 1;
      collaboratorSubText += `...+${collaboratorLength}`;
    }
    return collaboratorSubText;
  }


  _getCollabororInfo(name) {
    let { collaborators, canManageCollaborators } = store.getState().collaborators;
    collaborators = collaborators && collaborators[name];
    canManageCollaborators = canManageCollaborators && canManageCollaborators[name];
    return { collaborators, canManageCollaborators };
  }

  render() {
    const self = this,
          { props, state } = this,
          { sectionType } = props, // either labbook or dataset
          // get section from props
          section = props[sectionType],
          {
            name,
            owner,
          } = section,
          query = (sectionType === 'dataset') ? CollaboratorsDatasetQuery : CollaboratorsQuery,
          { collaborators, canManageCollaborators } = this._getCollabororInfo(name);

    return (
      <QueryRenderer
        query={query}
        environment={environment}
        variables={{
            name,
            owner,
          }}
        render={({ props, error }) => {
              if (props) {
                let section;
                section = sectionType === 'dataset' ? props.dataset : props.labbook;
                this.canManageCollaborators = section.canManageCollaborators;
                this.collaborators = section.collaborators;

                const collaboratorButtonCSS = classNames({
                    disabled: !section.canManageCollaborators && this.state.sessionValid,
                    'Collborators__btn Btn--flat Btn--no-underline': true,
                  }),

                  collaboratorCSS = classNames({
                    Collaborators: true,
                    disabled: !section.canManageCollaborators && this.state.sessionValid,
                  }),

                  collaboratorFilteredArr = section.collaborators && section.collaborators.filter(name => name !== owner);

                const collaboratorNames = self._getCollaboratorList(section.collaborators, collaboratorFilteredArr);

                return (

                  <div className={collaboratorCSS}>
                    <button
                      onClick={() => this._toggleCollaborators()}
                      className={collaboratorButtonCSS}>
                      Collaborators
                      <p className="BranchMenu__collaborator-names">{collaboratorNames}</p>
                    </button>

                    {
                      this.state.collaboratorModalVisible &&
                        <CollaboratorsModal
                          sectionType={this.props.sectionType}
                          key="CollaboratorsModal"
                          ref="collaborators"
                          collaborators={section.collaborators}
                          owner={owner}
                          labbookName={name}
                          toggleCollaborators={this._toggleCollaborators}
                        />

                    }
                  </div>
                );
              } else if (collaborators !== null) {
                const collaboratorButtonCSS = classNames({
                  disabled: !canManageCollaborators && this.state.sessionValid,
                  Collaborators__btn: true,
                });

                const collaboratorCSS = classNames({
                  Collaborators: true,
                  disabled: !canManageCollaborators && this.state.sessionValid,
                });

                const collaboratorFilteredArr = collaborators && collaborators.filter(name => name !== owner);

                const collaboratorNames = self._getCollaboratorList(collaborators, collaboratorFilteredArr);

                return (

                  <div className={collaboratorCSS}>
                    <button
                      onClick={() => this._toggleCollaborators()}
                      className={collaboratorButtonCSS}>
                      Collaborators
                      <p className="BranchMenu__collaborator-names">{collaboratorNames}</p>
                    </button>

                    {
                      this.state.collaboratorModalVisible &&

                        [<CollaboratorsModal
                          key="CollaboratorsModal"
                          ref="collaborators"
                          collaborators={collaborators}
                          owner={owner}
                          labbookName={name}
                          toggleCollaborators={this._toggleCollaborators}
                        />,
                          <div
                            key="CollaboratorsModal__cover"
                            className="modal__cover--nested"
                          />,
                        ]

                    }
                  </div>
                );
              }
                return (
                  <div className="Collaborators disabled">
                    <button
                      onClick={() => this.props.showLoginPrompt()}
                      className="Collaborators__btn disabled">
                      Collaborators
                     </button>
                  </div>
                );
          }}
      />

    );
  }
}

const mapStateToProps = (state, ownProps) => ({

});

const mapDispatchToProps = dispatch => ({
  setCollaborators,
  setCanManageCollaborators,
});

export default connect(mapStateToProps, mapDispatchToProps)(CollaboratorButton);
