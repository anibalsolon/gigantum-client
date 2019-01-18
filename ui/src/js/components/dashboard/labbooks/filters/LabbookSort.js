// vendor
import React, { Component } from 'react';
import classNames from 'classnames';
// assets
import './LabbookSort.scss';


class LabbookSort extends Component {
  constructor(props) {
    super(props);
    this._toggleSortMenu = this._toggleSortMenu.bind(this);
    this._closeFilterMenu = this._closeFilterMenu.bind(this);
  }

  state = {
    sortMenuOpen: false,
  }

  componentDidMount() {
    window.addEventListener('click', this._closeFilterMenu);
  }

  componentWillUnmount() {
    window.removeEventListener('click', this._closeFilterMenu);
  }

  /**
    *  @param {}
    *  closes toggle menu
    *  @return {}
  */
  _closeFilterMenu(evt) {
     if (evt.target.className.indexOf('LabbookSort') < 0) {
       this.setState({ sortMenuOpen: false });
     }
  }

  /**
    *  @param {}
    *  gets orderBy and sort value and displays it to the UI more clearly
    *  @return{}
  */
  _getSelectedSort() {
    if (this.props.orderBy === 'modified_on') {
      const modifiedDirection = this.props.sort === 'asc' ? '(Oldest)' : '(Newest)';
      return `Modified Date ${modifiedDirection}`;
    } else if (this.props.orderBy === 'created_on') {
      const creationDirection = this.props.sort === 'asc' ? '(Oldest)' : '(Newest)';
      return `Creation Date ${creationDirection}`;
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

    const labbookSortSeclectorCSS = classNames({
      LabbookSort__selector: true,
      'LabbookSort__selector--open': state.sortMenuOpen,
      'LabbookSort__selector--collapsed': !state.sortMenuOpen,
    });

    const labbookSortMenuCSS = classNames({
      'LabbookSort__menu box-shadow': true,
      hidden: !state.sortMenuOpen,
    });

    return (

      <div className="LabbookSort">
        Sort by:

        <span
          className={labbookSortSeclectorCSS}
          onClick={() => this._toggleSortMenu()}
        >
          {this._getSelectedSort()}
        </span>

        <ul className={labbookSortMenuCSS}>

          <li
            className="LabbookSort__list-item"
            onClick={() => props.setSortFilter('modified_on', 'desc')}
          >
            Modified Date (Newest) {state.orderBy === 'modified_on' && state.sort !== 'asc' ? '✓ ' : ''}
          </li>

          <li
            className="LabbookSort__list-item"
            onClick={() => props.setSortFilter('modified_on', 'asc')}
          >
            Modified Date (Oldest) {state.orderBy === 'modified_on' && state.sort === 'asc' ? '✓ ' : ''}
          </li>

          <li
            className="LabbookSort__list-item"
            onClick={() => props.setSortFilter('created_on', 'desc')}
          >
            Creation Date (Newest) {state.orderBy === 'created_on' && state.sort !== 'asc' ? '✓ ' : ''}
          </li>

          <li
            className="LabbookSort__list-item"
            onClick={() => props.setSortFilter('created_on', 'asc')}
          >
            Creation Date (Oldest) {state.orderBy === 'created_on' && state.sort === 'asc' ? '✓ ' : ''}
          </li>

          <li
            className="LabbookSort__list-item"
            onClick={() => props.setSortFilter('name', 'asc')}
          >
            A-Z {state.orderBy === 'name' && state.sort === 'asc' ? '✓ ' : ''}
          </li>

          <li
            className="LabbookSort__list-item"
            onClick={() => props.setSortFilter('name', 'desc')}
          >
            Z-A {this.state.orderBy === 'name' && this.state.sort !== 'asc' ? '✓ ' : ''}
          </li>

        </ul>

      </div>);
  }
}

export default LabbookSort;
