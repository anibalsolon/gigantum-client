// vendor
import React, { Component } from 'react';
import classNames from 'classnames';
// assets
import './DatasetSort.scss';


class DatasetSort extends Component {
  state = {
    sortMenuOpen: false,
  }

  /**
    *  @param {}
    *  gets orderBy and sort value and displays it to the UI more clearly
    *  @return{}
  */
  _getSelectedSort() {
    if (this.props.orderBy === 'modified_on') {
      return `Modified Date ${this.props.sort === 'asc' ? '(Oldest)' : '(Newest)'}`;
    } else if (this.props.orderBy === 'created_on') {
      return `Creation Date ${this.props.sort === 'asc' ? '(Oldest)' : '(Newest)'}`;
    }

    return this.props.sort === 'asc' ? 'A-Z' : 'Z-A';
  }

  /**
    *  @param {}
    *  update sort menu
    *  @return {}
  */
  _toggleSortMenu() {
    this.setState({ sortMenuOpen: !this.state.sortMenuOpen });
  }

  render() {
    const { props, state } = this;

    const datasetSortSeclectorCSS = classNames({
      DatasetSort__selector: true,
      'DatasetSort__selector--open': state.sortMenuOpen,
      'DatasetSort__selector--collapsed': !state.sortMenuOpen,
    });

    const datasetSortMenuCSS = classNames({
      'DatasetSort__menu box-shadow': true,
      hidden: !state.sortMenuOpen,
    });

    return (

      <div className="DatasetSort">
        Sort by:

        <span
          className={datasetSortSeclectorCSS}
          onClick={() => this._toggleSortMenu()}
        >
          {this._getSelectedSort()}
        </span>

        <ul className={datasetSortMenuCSS}>

          <li
            className="DatasetSort__list-item"
            onClick={() => props.setSortFilter('modified_on', 'desc')}
          >
            Modified Date (Newest) {state.orderBy === 'modified_on' && state.sort !== 'asc' ? '✓ ' : ''}
          </li>

          <li
            className="DatasetSort__list-item"
            onClick={() => props.setSortFilter('modified_on', 'asc')}
          >
            Modified Date (Oldest) {state.orderBy === 'modified_on' && state.sort === 'asc' ? '✓ ' : ''}
          </li>

          <li
            className="DatasetSort__list-item"
            onClick={() => props.setSortFilter('created_on', 'desc')}
          >
            Creation Date (Newest) {state.orderBy === 'created_on' && state.sort !== 'asc' ? '✓ ' : ''}
          </li>

          <li
            className="DatasetSort__list-item"
            onClick={() => props.setSortFilter('created_on', 'asc')}
          >
            Creation Date (Oldest) {state.orderBy === 'created_on' && state.sort === 'asc' ? '✓ ' : ''}
          </li>

          <li
            className="DatasetSort__list-item"
            onClick={() => props.setSortFilter('name', 'asc')}
          >
            A-Z {state.orderBy === 'name' && state.sort === 'asc' ? '✓ ' : ''}
          </li>

          <li
            className="DatasetSort__list-item"
            onClick={() => props.setSortFilter('name', 'desc')}
          >
            Z-A {this.state.orderBy === 'name' && this.state.sort !== 'asc' ? '✓ ' : ''}
          </li>

        </ul>

      </div>);
  }
}

export default DatasetSort;
