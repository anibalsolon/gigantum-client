// vendor
import React, { Component } from 'react';
import classNames from 'classnames';
// assets
import './DatasetFilterBy.scss';


class DatasetFilterBy extends Component {
  state = {
    filterMenuOpen: false,
  }

  /**
    *  @param {}
    *  gets filter value and displays it to the UI more clearly
  */
  _getFilter() {
    switch (this.props.filter) {
      case 'all':
        return 'All';
      case 'owner':
        return 'My Datasets';
      case 'others':
        return 'Shared With Me';
      default:
        return this.props.filter;
    }
  }

  /**
    *  @param {}
    *  update sort menu
    *  @return {}
  */
  _toggleFilterMenu() {
    this.setState({ filterMenuOpen: !this.state.filterMenuOpen });
  }

  render() {
    const { props, state } = this;

    const datasetFilterSeclectorCSS = classNames({
      DatasetFilterBy__selector: true,
      'DatasetFilterBy__selector--open': state.filterMenuOpen,
      'DatasetFilterBy__selector--collapsed': !state.filterMenuOpen,
    });

    const datasetFilterMenuCSS = classNames({
      'DatasetFilterBy__menu box-shadow': true,
      hidden: !state.filterMenuOpen,
    });

    return (

      <div className="DatasetFilterBy">
        Filter by:
        <span
          className={datasetFilterSeclectorCSS}
          onClick={() => this._toggleFilterMenu()}
        >
          {this._getFilter()}
        </span>
        <ul
          className={datasetFilterMenuCSS}
        >
          <li
            className="DatasetFilterBy__list-item"
            onClick={() => props.setFilter('all')}
          >
            All {props.filter === 'all' ? '✓ ' : ''}
          </li>
          <li
            className="DatasetFilterBy__list-item"
            onClick={() => props.setFilter('owner')}
          >
           My Datasets {props.filter === 'owner' ? '✓ ' : ''}
          </li>
          <li
            className="DatasetFilterBy__list-item"
            onClick={() => props.setFilter('others')}
          >
            Shared with me {props.filter === 'others' ? '✓ ' : ''}
          </li>
        </ul>
      </div>);
  }
}

export default DatasetFilterBy;
