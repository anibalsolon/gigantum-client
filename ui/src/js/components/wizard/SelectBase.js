// vendor
import React from 'react';
import { QueryRenderer, graphql } from 'react-relay';
import Slider from 'react-slick';
import classNames from 'classnames';
import ReactMarkdown from 'react-markdown';
// components
import Loader from 'Components/shared/Loader';
import AdvancedSearch from 'Components/shared/AdvancedSearch';
import BaseDetails from './BaseDetails';
// utilites
import environment from 'JS/createRelayEnvironment';


const BaseQuery = graphql`query SelectBaseQuery($first: Int!, $cursor: String){
  availableBases(first: $first, after: $cursor)@connection(key: "SelectBase_availableBases"){
    edges{
      node{
        id
        schema
        repository
        componentId
        revision
        name
        description
        readme
        tags
        icon
        osClass
        osRelease
        license
        url
        languages
        developmentTools
        installedPackages
        packageManagers
        dockerImageServer
        dockerImageNamespace
        dockerImageRepository
        dockerImageTag
      }
      cursor
    }
    pageInfo{
      endCursor
      hasNextPage
      hasPreviousPage
      startCursor
    }
  }
}`;

const DatasetQuery = graphql`query SelectBase_DatasetQuery{
  availableDatasets {
    id
    name
    storageType
    description
    isManaged
    readme
    tags
    icon
  }
}`;
export default class SelectBase extends React.Component {
  constructor(props) {
  	super(props);
  	this.state = {
      name: '',
      description: '',
      selectedBase: null,
      selectedBaseId: false,
      selectedTab: 'python3',
      viewedBase: null,
      viewingBase: false,
      tags: [],
    };

    this._backToBaseSelect = this._backToBaseSelect.bind(this);
    this._viewBase = this._viewBase.bind(this);
    this._selectBase = this._selectBase.bind(this);
    this._setTags = this._setTags.bind(this);
  }
  /**
    @param {object} edge
    takes a base image edge
    sets componest state for selectedBaseId and selectedBase
  */
  _selectBase(node) {
    this.setState({ selectedBase: node });
    this.setState({ selectedBaseId: node.id });
    this.props.selectBaseCallback(node);
    this.props.toggleDisabledContinue(false);
  }
  /**
    @param {object} edge
    takes a base image edge
    sets componest state for selectedBaseId and selectedBase
  */
  _viewBase(node) {
    this.setState({ viewedBase: node });
    this.setState({ viewingBase: true });

    this.props.toggleMenuVisibility(false);
  }

  _backToBaseSelect() {
    this.setState({ viewedBase: null });
    this.setState({ viewingBase: false });
    this.props.toggleMenuVisibility(true);
  }
  /**
    @param {}
    gets current selectedBase and passes variables to AddEnvironmentComponentMutation
    callback triggers and modal state is changed to  next window
  */
  continueSave() {
    this.props.toggleDisabledContinue(true);
    if (!this.props.datasets) {
      this.props.createLabbookMutation();
    } else {
      this.props.createDatasetMutation();
    }
  }
  /**
    @param {}
    @return {Object} environmentView
  */
  _environmentView() {
    return this.props.environmentView;
  }
  /**
    @param {}
    @return {}
  */
  _setSelectedTab(tab) {
    this.setState({ selectedTab: tab });
  }
  /**
    @param {array} availableBases
    sort bases into a object for easier consumption
    @return {object} sortedBases
  */
  _getTabStructure(availableBases) {
    const sortedBases = { tabs: [], bases: {} };
    availableBases.edges.forEach((edge) => {
      const languages = edge.node.languages;
      languages.forEach((language) => {
        if (sortedBases.tabs.indexOf(language) < 0) {
          sortedBases.tabs.push(language);
          sortedBases.bases[language] = [edge.node];
        } else {
          sortedBases.bases[language].push(edge.node);
        }
      });
    });

    return sortedBases;
  }
  /**
    @param {object} datasetBases
    determines filter criteria for dataset types
    @return {object} filters
  */
  _createFilters(datasetBases) {
    const filters = {
      'Dataset Type': ['Managed', 'Unmanaged'],
      Tags: [],
    };
    const tags = new Set();
    datasetBases.forEach((datasetBase) => {
      datasetBase.tags.forEach((tag) => {
        if (!tags.has(tag)) {
          tags.add(tag);
        }
      });
    });
    filters.Tags = Array.from(tags);
    return filters;
  }
  /**
    @param {Array} tags
    sets component tags from child
  */
  _setTags(tags) {
    this.setState({ tags });
  }
  /**
    @param {Array} datasets
    filters datasets based on selected filters
  */
  _filterDatasets(datasets) {
    const tags = this.state.tags.map(tagObject => tagObject.text.toLowerCase());
    return datasets.filter((dataset) => {
      const lowercaseReadme = dataset.readme.toLowerCase();
      const lowercaseDescription = dataset.description.toLowerCase();
      const lowercaseName = dataset.name.toLowerCase();
      let isReturned = true;
      if (tags.indexOf('Managed') > -1 && !dataset.isManaged ||
          tags.indexOf('Unmanaged') > -1 && dataset.isManaged) {
        isReturned = false;
      }

      tags.forEach((tag) => {
        if (tag !== 'Managed' && tag !== 'Unmanaged' &&
            dataset.tags.indexOf(tag) === -1 &&
            lowercaseReadme.indexOf(tag) === -1 &&
            lowercaseDescription.indexOf(tag) === -1 &&
            lowercaseName.indexOf(tag) === -1) {
          isReturned = false;
        }
      });
      return isReturned;
    });
  }


  render() {
    const sliderSettings = {
      dots: false,
      infinite: false,
      speed: 500,
      slidesToShow: 2,
      slidesToScroll: 1,
      arrows: false,
    };
    const variables = {
      first: 20,
    };

    const innerContainer = classNames({
      'SelectBase__inner-container': true,
      'SelectBase__inner-container--datasets': true,
      'SelectBase__inner-container--viewer': this.state.viewingBase,
    });

    return (
      <div className="SelectBase">
        <QueryRenderer
          variables={this.props.datasets ? {} : variables}
          query={this.props.datasets ? DatasetQuery : BaseQuery}
          environment={environment}
          render={({ error, props }) => {
              if (error) {
                return (<div>{error.message}</div>);
              }

                if (props && !this.props.datasets) {
                  const sortedBaseItems = this._getTabStructure(props.availableBases);
                  const selecBaseImage = classNames({
                    SelectBase__images: true,
                    'SelectBase__images--hidden': (this.state.selectedTab === 'none'),
                  });

                  if (sortedBaseItems.bases[this.state.selectedTab].length > 2) sliderSettings.arrows = true;
                  return (
                    <div className={innerContainer}>
                      <div className="SelectBase__select-container">
                        <div className="SelectBase__tabs-container">
                          <ul className="SelectBase__tabs-list">
                            {
                              sortedBaseItems.tabs.map(tab => (
                                <LanguageTab
                                  key={tab}
                                  tab={tab}
                                  self={this}
                                  length={sortedBaseItems.bases[tab].length}
                                />))
                            }
                          </ul>
                        </div>
                        <div className={selecBaseImage}>
                          <Slider {...sliderSettings}>
                            {
                              (this.state.selectedTab !== 'none') && sortedBaseItems.bases[this.state.selectedTab].map(node => (
                                <div
                                  key={node.id}
                                  className="BaseSlide__wrapper"
                                >
                                  <BaseSlide
                                    key={`${node.id}_slide`}
                                    node={node}
                                    self={this}
                                  />
                                </div>
                                  ))
                            }
                          </Slider>

                        </div>
                      </div>
                      <div className="SelectBase__viewer-container">
                        <BaseDetails
                          base={this.state.viewedBase}
                          backToBaseSelect={this._backToBaseSelect}
                        />
                      </div>

                    </div>
                  );
                } else if (props && this.props.datasets) {
                  const filterCategories = this._createFilters(props.availableDatasets);
                  const filteredDatasets = this._filterDatasets(props.availableDatasets);
                  return <div className={innerContainer}>
                    <AdvancedSearch
                      tags={this.state.tags}
                      setTags={this._setTags}
                      filterCategories={filterCategories}
                    />
                    <div className="SelectBase__select-container">
                      <div className="SelectBase__images">
                        {
                          filteredDatasets.map(node => (
                            <div
                              key={node.id}
                              className="BaseSlide__wrapper"
                            >
                              <DatasetSlide
                                key={`${node.id}_slide`}
                                node={node}
                                self={this}
                              />
                            </div>
                              ))
                        }
                      </div>
                    </div>
                    <div className="SelectBase__viewer-container">
                      <BaseDetails
                        base={this.state.viewedBase}
                        backToBaseSelect={this._backToBaseSelect}
                        datasets={this.props.datasets}
                      />
                    </div>

                  </div>;
                }
                  return (<Loader />);
          }}
        />

      </div>
    );
  }
}

/**
* @param {string, this}
* returns tab jsx for
* return {jsx}
*/
const LanguageTab = ({ tab, self, length }) => {
  const tabClass = classNames({
    SelectBase__tab: true,
    'SelectBase__tab--selected': (tab === self.state.selectedTab),
  });
  return (<li
    className={tabClass}
    onClick={() => self._setSelectedTab(tab)}
  >
    {`${tab} (${length})`}
          </li>);
};

/**
* @param {string, this}
* returns base slide
* return {jsx}
*/
const BaseSlide = ({ node, self }) => {
  const selectedBaseImage = classNames({
    SelectBase__image: true,
    'SelectBase__image--selected': (self.state.selectedBaseId === node.id),
  });
  return (<div
    onClick={() => self._selectBase(node)}
    className="SelectBase__image-wrapper slick-slide"
  >
    <div
      className={selectedBaseImage}
    >
      <div className="SelectBase__image-icon">
        <img
          alt=""
          src={node.icon}
          height="50"
          width="50"
        />
      </div>
      <div className="SelectBase__image-text">
        <h6 className="SelectBase__image-header">{node.name}</h6>
        <p>{`${node.osClass} ${node.osRelease}`}</p>
        <p className="SelectBase__image-description">{node.description}</p>

        <div className="SelectBase__image-info">
          <div className="SelectBase__image-languages">
            <h6>Languages</h6>
            <ul>
              {
              node.languages.map(language => (<li key={language}>{language}</li>))
            }
            </ul>
          </div>
          <div className="SelectBase__image-tools">
            <h6>Tools</h6>
            <ul>
              {
              node.developmentTools.map(tool => (<li key={tool}>{tool}</li>))
            }
            </ul>
          </div>
        </div>
        <div className="SelectBase__image-actions">
          <button onClick={() => self._viewBase(node)} className="button--flat">View Details</button>
        </div>
      </div>
    </div>
  </div>);
};

/**
* @param {string, this}
* returns dataset slide
* return {jsx}
*/
const DatasetSlide = ({ node, self }) => {
  const selectedBaseImage = classNames({
    SelectBase__image: true,
    'SelectBase__image--selected': (self.state.selectedBaseId === node.id),
    Card: true,
  });
  const actionCSS = classNames({
    'SelectBase__image-actions': true,
    'SelectBase__image-actions--expanded': self.state.expandedNode === node.name,
  });
  return (<div
    onClick={evt => evt && evt.target.className.indexOf('button--flat') === -1 && self._selectBase(node)}
    className="SelectBase__image-wrapper"
  >
    <div
      className={selectedBaseImage}
    >
      <div className="SelectBase__image-icon">
        <img
          alt=""
          src={`data:image/jpeg;base64,${node.icon}`}
          height="50"
          width="50"
        />
      </div>
      <div className="SelectBase__details">
        <h6 className="SelectBase__name">{node.name}</h6>
        <h6 className="SelectBase__type">{node.isManaged ? 'Managed' : 'Unmanaged'}</h6>
      </div>
      <div className="SelectBase__image-text">
        <p className="SelectBase__image-description">{node.description}</p>
        {
          self.state.expandedNode === node.name &&
          <ReactMarkdown source={node.readme} />
        }
      </div>
      <div className={actionCSS}>
        <button onClick={() => self.setState({ expandedNode: self.state.expandedNode === node.name ? null : node.name })} className="button--flat"></button>
      </div>
    </div>
  </div>);
};
