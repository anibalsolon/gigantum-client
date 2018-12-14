
      import React, { Component } from 'react';
      import renderer from 'react-test-renderer';
      import { mount } from 'enzyme';
      import MostRecentInput from 'Components/labbook/filesShared/MostRecentInput';
      import store from 'JS/redux/store';

      import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';

      import relayTestingUtils from '@gigantum/relay-testing-utils';
      import json from './__relaydata__/MostRecentInput.json';


      const fixtures = {
        edgeId: json.data.labbook.input.id,
        input: json.data.labbook.input,
      };

      store.dispatch({
        type: 'UPDATE_CALLBACK_ROUTE',
        payload: {
          callbackRoute: '/labbooks/username/labbookName/inputData',
        },
      });

      class MostRecentInputComponent extends Component {
        render() {
          return (relayTestingUtils.relayWrap(<MostRecentInput {...fixtures}/>, {}, json.data.labbook.input));
        }
      }

      describe('Test MostRecentInput', () => {
        it('render snapshot', () => {
          const wrapper = renderer.create(

            <Router>
               <Switch>
               <Route
                 path=""
                 render={() => <MostRecentInputComponent />
                 }
               />
             </Switch>
            </Router>,

          );

          const tree = wrapper.toJSON();

          expect(tree).toMatchSnapshot();
        });
      });
