
      import React from 'react';
      import renderer from 'react-test-renderer';
      import { mount } from 'enzyme';
      import Collaborators from 'Components/labbook/branchMenu/collaborators/Collaborators';


      import relayTestingUtils from '@gigantum/relay-testing-utils';

      import Promise from 'promise';
      import json from './__relaydata__/Collaborators.json';

      import config from '../../../../config';


      let promise = new Promise((resolve) => { resolve(true); });
      const { owner, labbookName } = config;


      const showLoginPrompt = () => {

      };

      describe('Test Collaborators', () => {
        it('renders valid', () => {
          let checkSessionIsValid = isValid => promise.then(isValid => true);

          let fixtures = {
              key: 'test_collaborators',
              owner,
              labbookName,
              checkSessionIsValid,
              showLoginPrompt,
          };

          const wrapper = renderer.create(

             relayTestingUtils.relayWrap(
               <Collaborators {...fixtures} />, {}, json.data.collaborators,
             ),

          );

          const tree = wrapper.toJSON();

          expect(tree).toMatchSnapshot();
       });


       it('renders invalid', () => {
         let checkSessionIsValid = isValid => promise.then(isValid => false);

         let fixtures = {
             key: 'test_collaborators',
             owner,
             labbookName,
             checkSessionIsValid,
             showLoginPrompt,
         };

         const wrapper = renderer.create(

            relayTestingUtils.relayWrap(
              <Collaborators {...fixtures} />, {}, json.data.collaborators,
            ),

         );

         const tree = wrapper.toJSON();

         expect(tree).toMatchSnapshot();
      });
      });
