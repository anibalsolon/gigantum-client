import dispatcher from 'JS/redux/dispatcher';

/**
 * constants
 */
export const TOGGLE_PACKAGE_MENU = 'TOGGLE_PACKAGE_MENU';

/**
 * actions
 */
export const setPackageMenuVisible = packageMenuVisible => dispatcher(TOGGLE_PACKAGE_MENU, { packageMenuVisible });


export default (
  state = { packageMenuVisible: false },
  action,
) => {
  if (action.type === TOGGLE_PACKAGE_MENU) {
    return {
      ...state,
      packageMenuVisible: action.payload.packageMenuVisible,
    };
  }
  return state;
};
